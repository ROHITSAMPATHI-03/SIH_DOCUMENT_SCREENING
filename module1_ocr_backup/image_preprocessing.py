import cv2


def preprocess_image(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not find image: {image_path}"
        )

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Resize image
    scale = 2

    resized = cv2.resize(
        gray,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )

    # Light noise reduction
    processed = cv2.GaussianBlur(
        resized,
        (3, 3),
        0
    )

    return processed