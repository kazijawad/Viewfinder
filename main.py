# Based after OpenCV DNN Text Detection Skeleton: https://github.com/opencv/opencv/tree/master/samples/dnn

# Import required modules
import argparse
import math
import cv2 as cv

# Temporary Command Line Interface
parser = argparse.ArgumentParser(description="Runs the EAST model for OCR")
parser.add_argument("--model",
                    default="./test_model/frozen_east_text_detection.pb",
                    help="Path to a binary .pb file of model")
args = parser.parse_args()

# Analyzes images for text
def analyzer(geometry, scores, scoreThreshold):
    detections = []
    confidences = []
    height = scores.shape[2]
    width = scores.shape[3]

    for y in range(0, height):
        data = scores[0][0][y]
        x0 = geometry[0][0][y]
        x1 = geometry[0][1][y]
        x2 = geometry[0][2][y]
        x3 = geometry[0][3][y]
        angles = geometry[0][4][y]

        for x in range(0, width):
            score = data[x]
            if score < scoreThreshold:
                continue

            offsetX = x * 4.0
            offsetY = y * 4.0
            angle = angles[x]

            cosA = math.cos(angle)
            sinA = math.sin(angle)
            boundH = x0[x] + x2[x]
            boundW = x1[x] + x3[x]

            offset = ([offsetX + cosA * x1[x] + sinA * x2[x],
                        offsetY - sinA * x1[x] + cosA * x2[x]])

            point1 = (-sinA * boundH + offset[0],
                        -cosA * boundH + offset[1])
            point3 = (-cosA * boundW + offset[0],
                        sinA * boundW + offset[1])
            center = (0.5 * (point1[0] + point3[0]),
                        0.5 * (point1[1] + point3[1]))

            detections.append((center, (boundW, boundH),
                                -1 * angle * 180.0 / math.pi))
            confidences.append(float(score))

    return [detections, confidences]

# Executes model for OCR
def main():
    model = args.model
    inputHeight = 320
    inputWidth = 320
    confidenceThreshold = 0.5
    nmsThreshold = 0.4

    network = cv.dnn.readNet(model)
    cv.namedWindow("Viewfinder", cv.WINDOW_NORMAL)

    cap = cv.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting ...")
            break

        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]
        resizedHeight = frameHeight / float(inputHeight)
        resizedWidth = frameWidth / float(inputWidth)

        blob = cv.dnn.blobFromImage(frame, 1.0, (inputWidth, inputHeight),
                                    (123.68, 116.78, 103.94), True, False)

        network.setInput(blob)
        outputs = network.forward(["feature_fusion/Conv_7/Sigmoid",
                                   "feature_fusion/concat_3"])

        geometry = outputs[1]        
        scores = outputs[0]
        [boundingBoxes, confidences] = analyzer(geometry, scores,
                                                confidenceThreshold)

        indexes = cv.dnn.NMSBoxesRotated(boundingBoxes, confidences,
                                         confidenceThreshold, nmsThreshold)
        for i in indexes:
            vertices = cv.boxPoints(boundingBoxes[i[0]])

            for j in range(4):
                vertices[j][0] *= resizedWidth
                vertices[j][1] *= resizedHeight
            
            for j in range(4):
                point1 = (vertices[j][0], vertices[j][1])
                point2 = (vertices[(j + 1) % 4][0], vertices[(j + 1) % 4][1])
                cv.line(frame, point1, point2, (0, 0, 255), 2)

        cv.imshow("Viewfinder", frame)
        if cv.waitKey(1) == ord("q"):
            break

if __name__ == "__main__":
    main()
