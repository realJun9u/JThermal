import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

# For webcam input:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
cap = cv2.VideoCapture(0)
with mp_face_mesh.FaceMesh(
   max_num_faces=1,
   refine_landmarks=True,
   min_detection_confidence=0.5,
   min_tracking_confidence=0.5) as face_mesh:
   print(cv2.__version__)
   cv2.namedWindow("Img")
   while cap.isOpened():
      success, image = cap.read()
      if not success:
         print("Ignoring empty camera frame.")
         # If loading a video, use 'break' instead of 'continue'.
         continue
      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      print("Before face_mesh.process")
      results = face_mesh.process(image)
      print("After face_mesh.process")
   
      # Draw the face mesh annotations on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      print("Before face_landmarks drawing")
      if results.multi_face_landmarks:
         for face_landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(
               image=image,
               landmark_list=face_landmarks,
               connections=mp_face_mesh.FACEMESH_TESSELATION,
               landmark_drawing_spec=None,
               connection_drawing_spec=mp_drawing_styles
               .get_default_face_mesh_tesselation_style())
            mp_drawing.draw_landmarks(
               image=image,
               landmark_list=face_landmarks,
               connections=mp_face_mesh.FACEMESH_CONTOURS,
               landmark_drawing_spec=None,
               connection_drawing_spec=mp_drawing_styles
               .get_default_face_mesh_contours_style())
            mp_drawing.draw_landmarks(
               image=image,
               landmark_list=face_landmarks,
               connections=mp_face_mesh.FACEMESH_IRISES,
               landmark_drawing_spec=None,
               connection_drawing_spec=mp_drawing_styles
               .get_default_face_mesh_iris_connections_style())
      print("After face_landmarks drawing")
      # Flip the image horizontally for a selfie-view display.
      image = cv2.flip(image,1)
      print("After cv2.flip")
      cv2.imwrite("test.jpg",image)
      print("After cv2.imwrite")
      cv2.imshow("FaceMesh", image)
      print("After cv2.imshow")
      if cv2.waitKey(50) == 27:
         break
print("Exit")
cv2.destroyAllWindows()
cap.release()
