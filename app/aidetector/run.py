import onnxruntime as ort
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np
import time, sys, subprocess, datetime, os, json

def image_to_tensor(image_path):
    # Load the image
    image = Image.open(image_path)
    orig_w, orig_h = image.size

    # Resize the image to the required size (416x416)
    resized_image = image.resize((416, 416))

    # Convert the image to RGB (3 channels)
    if resized_image.mode != 'RGB':
        resized_image = resized_image.convert('RGB')

    # Convert the image to a numpy array and normalize it
    image_array = np.array(resized_image).astype(np.float32) / 255.0

    # Change the shape of the numpy array to match the input shape of the model ([1, 3, 416, 416])
    # This involves moving the color channel to the second dimension and adding an extra dimension at the start
    input_tensor = np.transpose(image_array, (2, 0, 1))
    input_tensor = np.expand_dims(input_tensor, axis=0)

    return input_tensor, orig_w, orig_h

def show_matching_boxes(boxes, confs, image_width=416, image_height=416, threshold=0.1):
    # Iterate over boxes and confidences
    for i, box in enumerate(boxes):
        # Extract the confidence score
        conf = confs[i][0]

        # Check if the confidence score is greater than the threshold
        if conf > threshold:
            # Extract and adjust bounding box coordinates
            x_min, y_min, x_max, y_max = box[0]
            x_min_pixel = int(x_min * image_width)
            y_min_pixel = int(y_min * image_height)
            x_max_pixel = int(x_max * image_width)
            y_max_pixel = int(y_max * image_height)

            # Print the adjusted bounding box and its confidence score
            print(f"Box: {x_min_pixel}, {y_min_pixel}, {x_max_pixel}, {y_max_pixel}, Confidence: {conf}")

def overlapping_box(xmax1, xmin2, xmax2, xmin1):
    return xmax1 >= xmin2 and xmax2 >= xmin1

# Draw a box on the area with the maxium confidence score. Take the
# orignal image path and the output path of the new processed image.
# The threshold argument is used to write no box at all if the confidence
# is less than the specified amount.
def draw_boxes(image_path, output_path, boxes, confidences, threshold=0.1):
    # Load the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Define font for confidence score
    # Calculate font size as a proportion of image width
    font_size = max(18,min(int(image.width // 20), int(image.height // 20)))
    try:
        font = ImageFont.truetype("./bedstead.otf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Iterate over the bounding boxes and confidences
    sorted_boxes = sorted(zip(boxes, confidences), key=lambda x: x[1][0], reverse=True)

    max_draw_boxes = 5
    already_drawn_boxes = []
    for box, confidence in sorted_boxes:
        if already_drawn_boxes.__len__() >= max_draw_boxes:
            break
        confidence = confidence[0]
        if confidence < threshold:
            continue

        x_min, y_min, x_max, y_max = box[0]
        x_min *= image.width
        y_min *= image.height
        x_max *= image.width
        y_max *= image.height

        # dont draw boxes that are too close to each other
        can_draw = True
        for drawn_box in already_drawn_boxes:
            drawn_box_x_min = drawn_box[0]
            drawn_box_y_min = drawn_box[1]
            drawn_box_x_max = drawn_box[2]
            drawn_box_y_max = drawn_box[3]

            if overlapping_box(x_max, drawn_box_x_min, drawn_box_x_max, x_min) and overlapping_box(y_max, drawn_box_y_min, drawn_box_y_max, y_min):
                can_draw = False
                break

        if can_draw == True:
            draw.rectangle([x_min,y_min,x_max,y_max], outline="red", width=2)

            # Draw the confidence score
            score_text = f"{confidence:.2f}"
            draw.text((x_min,y_min), score_text, fill="red", font=font)
            already_drawn_boxes.append([x_min, y_min, x_max, y_max])

    # Write the current time as well.
    draw.text((20,20), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fill="green", font=font)

    # Save or display the image
    image.save(output_path)
    # image.show()

def show_model_info(model_path):
    import onnx
    model = onnx.load(model_path)
    print("Model Inputs:")
    for input in model.graph.input:
        print("  Name:", input.name)
        # The shape of the input tensor
        print("  Shape:", [dim.dim_value for dim in input.type.tensor_type.shape.dim])
        # Data type of the input tensor
        print("  Data type:", input.type.tensor_type.elem_type)

    print("Model Outputs:")
    for output in model.graph.output:
        print("  Name:", output.name)
        # The shape of the input tensor
        print("  Shape:", [dim.dim_value for dim in output.type.tensor_type.shape.dim])
        # Data type of the input tensor
        print("  Data type:", output.type.tensor_type.elem_type)

    # Calculate the total number of parameters
    total_params = 0
    for initializer in model.graph.initializer:
        # Each initializer is a tensor containing parameters for a layer
        params = 1
        for dim in initializer.dims:
            params *= dim
        total_params += params
    print("Total number of parameters:", total_params)

# Evaluate the specified image, return the max score of the
# different identified boxes of failure and as side effect create a new
# image with the highlighted boxes.
def evaluate_image(inference_session,in_image_path,out_image_path, threshold=0.1):
    # Load and preprocess the input image inputTensor
    inputTensor,orig_w,orig_h = image_to_tensor(in_image_path)

    # Run inference
    start_time = time.time()
    outputs = inference_session.run(None, {"input": inputTensor})
    end_time = time.time()
    duration_time = (end_time - start_time)*1000
    print("Neural network inference milliseconds runtime: ", duration_time)

    boxes = outputs[0][0]
    confs = outputs[1][0]
    show_matching_boxes(boxes,confs,image_width=orig_w,image_height=orig_h,threshold=threshold)
    draw_boxes(in_image_path,out_image_path,boxes,confs,threshold=threshold)
    max_score = 0
    for item in confs:
        if item[0] > max_score: max_score = item[0]

    sorted_boxes = sorted(zip(boxes, confs), key=lambda x: x[1][0], reverse=True)

    score_data = {
        "max_score": str(max_score),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "threshold": str(threshold)
    }

    return score_data

def process_single(image_path):
    model_path = "./model-weights-5a6b1be1fa.onnx"
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    max_score = evaluate_image(session,image_path,"processed.png")
    print("Max score:", max_score)

def write_file(filename, content):
    f = open(filename,"w")
    f.write(content)
    f.close()

def main():
    print("Starting...")
    refresh_rate = int(os.getenv("ALL_REFRESH_RATE", "30"))
    model_path = "./model-weights-5a6b1be1fa.onnx"
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    while True:
        fetched_filename = "".join(["/tmp/fetched_",str(time.time()),".jpg"])
        streamer_printer_hostname = os.getenv("STREAMER_PRINTER_ADDRESS", "localhost")
        streamer_access_token = os.getenv("STREAMER_PRINTER_ACCESS_CODE")
        fetch_image_command = ["python3", "/app/streamer/run.py", streamer_printer_hostname, streamer_access_token, fetched_filename]
        # Fetch the image using the user provided command.
        print("Executing ", " ".join(fetch_image_command))
        process = subprocess.run(fetch_image_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        error_code = process.returncode
        if error_code != 0:
            print("Warning: Fetch image script exited with an error: ", error_code)
            if os.path.exists("/app/web/last_image.png"):
                os.remove("/app/web/last_image.png")
            if os.path.exists("/app/web/last_score_data.json"):
                os.remove("/app/web/last_score_data.json")
        else:
            print("Processing image...")
            score_data = evaluate_image(session,fetched_filename,"".join([fetched_filename,".processed.png"]))
            score_data["image_path"] = "".join([fetched_filename,".processed.png"])
            score_data["refresh_rate"] = refresh_rate
            json_score_data = json.dumps(score_data)
            write_file("/app/web/last_score_data.json", json_score_data)
            os.replace("".join([fetched_filename,".processed.png"]), "/app/web/last_image.png")

        time.sleep(refresh_rate)

if __name__ == "__main__":
    main()