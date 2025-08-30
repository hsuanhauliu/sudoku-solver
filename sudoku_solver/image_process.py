import cv2
import numpy as np
import pytesseract


def extract_sudoku_board(image_path):
    # 1. Preprocess the image
    original_img, thresh = preprocess_image(image_path)
    if original_img is None:
        return

    # 2. Find the Sudoku grid
    grid_contour = find_grid_contour(thresh)
    if grid_contour is None:
        print("Could not find a Sudoku grid in the image.")
        return
    
    cv2.drawContours(original_img, [grid_contour], -1, (0, 255, 0), 2)

    # 3. Apply perspective transform
    warped_grid, _ = get_perspective_transform(original_img, grid_contour)

    # 4. Extract digits
    return extract_digits_from_grid(warped_grid)
 

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

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 3)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return img, thresh

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

def extract_digits_from_grid(warped_grid):
    """Extracts each digit from the grid cells using Tesseract OCR."""
    board = np.zeros((9, 9), dtype=int)
    gray_warped = cv2.cvtColor(warped_grid, cv2.COLOR_BGR2GRAY)
    
    cell_height = gray_warped.shape[0] // 9
    cell_width = gray_warped.shape[1] // 9

    for r in range(9):
        for c in range(9):
            # Crop the cell from the warped grid
            y1, y2 = r * cell_height, (r + 1) * cell_height
            x1, x2 = c * cell_width, (c + 1) * cell_width
            
            # Create a margin to remove grid lines from the cell
            margin = 5
            cell_roi = gray_warped[y1 + margin:y2 - margin, x1 + margin:x2 - margin]

            # If the cell ROI is too small after margin, skip it
            if cell_roi.shape[0] < 10 or cell_roi.shape[1] < 10:
                continue
            
            # Apply thresholding to isolate the digit
            _, cell_thresh = cv2.threshold(cell_roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

            # Find contours in the thresholded cell
            contours, _ = cv2.findContours(cell_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Find the largest contour, assuming it's the digit
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Filter out small noise contours
                contour_area = cv2.contourArea(largest_contour)
                min_area = 20 # Adjust this threshold based on image resolution
                
                if contour_area > min_area:
                    # Create a mask for the largest contour to isolate the digit
                    mask = np.zeros(cell_thresh.shape, dtype=np.uint8)
                    cv2.drawContours(mask, [largest_contour], -1, 255, -1)
                    
                    # Extract the digit using the mask
                    digit_only = cv2.bitwise_and(cell_thresh, cell_thresh, mask=mask)

                    # Add padding to improve OCR accuracy
                    border_size = 10
                    cell_padded = cv2.copyMakeBorder(digit_only, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=0)

                    # Use Tesseract to recognize the digit
                    custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=123456789'
                    try:
                        digit_str = pytesseract.image_to_string(cell_padded, config=custom_config).strip()
                        if digit_str.isdigit():
                            board[r, c] = int(digit_str)
                    except pytesseract.TesseractNotFoundError:
                        print("Tesseract Error: The Tesseract executable was not found.")
                        print("Please make sure it's installed and configured correctly in the script.")
                        return None
                    except Exception:
                        # Ignore other potential OCR errors for empty cells
                        pass
    return board

def _debug_show_img(img):
    cv2.imshow("debug", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
