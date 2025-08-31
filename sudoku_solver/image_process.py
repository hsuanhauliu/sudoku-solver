import os
import urllib.request

import cv2
import numpy as np
import pytesseract

def download_model(model_file="mnist.onnx"):
    """Downloads the pre-trained ONNX model if it doesn't exist."""
    if not os.path.exists(model_file):
        print("Downloading pre-trained digit recognition model (mnist.onnx)...")
        # A reliable link to a simple MNIST ONNX model
        url = "https://github.com/onnx/models/raw/refs/heads/main/validated/vision/classification/mnist/model/mnist-12.onnx"
        try:
            urllib.request.urlretrieve(url, model_file)
            print(f"Model download complete: {model_file}")
        except Exception as e:
            print(f"Error downloading model: {e}")
            return None
    return model_file

def extract_sudoku_board(image_path, model_path, debug=False):
    try:
        net = cv2.dnn.readNetFromONNX(model_path)
    except Exception as e:
        print(f"Error loading the ONNX model: {e}")
        return None

    # 1. Preprocess the image
    original_img, thresh = preprocess_image(image_path)
    if original_img is None:
        return None
    if debug:
        _debug_show_img(original_img, "original img")
        _debug_show_img(thresh, "gray scaled")

    # 2. Find the Sudoku grid
    grid_contour = find_grid_contour(thresh)
    if grid_contour is None:
        print("Could not find a Sudoku grid in the image.")
        return None
    
    cv2.drawContours(original_img, [grid_contour], -1, (0, 255, 0), 2)
    if debug:
        _debug_show_img(original_img, "with contour")

    # 3. Apply perspective transform
    warped_grid, _ = get_perspective_transform(original_img, grid_contour)
    if debug:
        _debug_show_img(warped_grid, "warped grid")

    # 4. Extract digits
    return extract_digits_from_grid(warped_grid, net, debug=debug)
 

def preprocess_image(image_path):
    """Loads and preprocesses the image for grid detection."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

    # Resize for consistent processing
    scale = 600 / img.shape[1]
    img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))

    blurred_color = cv2.bilateralFilter(img, 9, 75, 75)
    gray = cv2.cvtColor(blurred_color, cv2.COLOR_BGR2GRAY)

    # Adaptive gaussian thresholing seems to work better for our case, since the board is usually clean.
    # https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return blurred_color, thresh

def find_grid_contour(thresh_image):
    """Finds the largest contour that is likely the Sudoku grid."""
    contours, _ = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Sort contours by area in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # The grid should be the largest quadrilateral contour
    for c in contours:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        if len(approx) == 4:
            return approx
    return None

def order_points(pts):
    """Orders the 4 points of the contour in top-left, top-right, bottom-right, bottom-left order."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def get_perspective_transform(image, corners):
    """Applies a perspective transform to get a top-down view of the grid."""
    ordered_corners = order_points(corners.reshape(4, 2))
    tl, tr, br, bl = ordered_corners

    # Determine the width of the new image
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))
    
    # Determine the height of the new image
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    # Define the destination points for the warped image
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")

    # Compute the perspective transform matrix and warp the image
    matrix = cv2.getPerspectiveTransform(ordered_corners, dst)
    warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
    return warped, matrix

def extract_digits_from_grid(warped_grid, model, debug=False):
    """Extracts each digit from the grid cells using a CNN model."""
    board = np.zeros((9, 9), dtype=int)
    
    # Resize the grid to a fixed size for consistent processing
    fixed_size = 450
    grid_resized = cv2.resize(warped_grid, (fixed_size, fixed_size))
    gray_resized = cv2.cvtColor(grid_resized, cv2.COLOR_BGR2GRAY)
    
    cell_size = fixed_size // 9
    margin = 5 # Number of pixels to crop from each side of the cell

    for r in range(9):
        for c in range(9):
            # Crop the cell from the grid, removing the border via the margin.
            y1 = r * cell_size + margin
            y2 = (r + 1) * cell_size - margin
            x1 = c * cell_size + margin
            x2 = (c + 1) * cell_size - margin
            cell_cropped = gray_resized[y1:y2, x1:x2]

            # Apply thresholding to get a binary image of the digit.
            _, cell_thresh = cv2.threshold(cell_cropped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

            # Check if the cell contains a digit by looking for non-zero pixels
            if cv2.countNonZero(cell_thresh) > 20:
                
                # Prepare the cell for the deep learning model
                # The model expects a 28x28 image
                roi = cv2.resize(cell_thresh, (28, 28))
                
                # Create a blob for the DNN model
                # Normalization (1/255.0) and creating the blob
                blob = cv2.dnn.blobFromImage(roi, 1.0 / 255.0, (28, 28))
                
                # Set the input to the network and perform a forward pass
                model.setInput(blob)
                pred = model.forward()
                
                # Get the digit with the highest probability
                digit = np.argmax(pred)
                if debug:
                    print(digit)
                    _debug_show_img(cell_cropped)
                
                # Sudoku doesn't use '0', so we can ignore it to filter out noise.
                if digit != 0:
                    board[r, c] = digit
    return board

def _debug_show_img(img, window_name="debug"):
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
