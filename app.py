import numpy as np
import cv2
import streamlit as st
from tensorflow import keras
from keras.models import model_from_json
from keras.preprocessing.image import img_to_array
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration, VideoProcessorBase, WebRtcMode

# load model
emotion_dict = {0:'angry', 1 :'happy', 2: 'neutral', 3:'sad', 4: 'surprise'}
# load json and create model
json_file = open('emotion_model1.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
classifier = model_from_json(loaded_model_json)

# load weights into new model
classifier.load_weights("emotion_model1.h5")

#load face
try:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
except Exception:
    st.write("Error loading cascade classifiers")

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

class Faceemotion(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        #dst = cv2.resize(img, (800, 400))
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        #image gray
        #img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            image=img_gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces:
            #cv2.rectangle(img=img, pt1=(x, y), pt2=(
            #    x + w, y + h), color=(255, 0, 0), thickness=2)
            cv2.rectangle(img=small_frame, pt1=(x, y), pt2=(
                x + w, y + h), color=(255, 0, 0), thickness=2)
            roi_gray = img_gray[y:y + h, x:x + w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype('float') / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)
                prediction = classifier.predict(roi)[0]
                maxindex = int(np.argmax(prediction))
                finalout = emotion_dict[maxindex]
                output = str(finalout)
            label_position = (x, y)
            #cv2.putText(img, output, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(small_frame, output, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        #return img
        return small_frame

def main():
    # Face Analysis Application #
    st.title("認知症予防AIアプリ")
    activiteis = ["Home", "身体機能：表情検出"]
    choice = st.sidebar.selectbox("Select Activity", activiteis)
    st.sidebar.markdown(
        """ Developed by 尾松紀依・佐藤能臣    
            Email : yas-sato@clinks.jp  """)
    if choice == "Home":
        html_temp_home1 = """<div style="background-color:#6D7B8D;padding:10px">
                                            <h4 style="color:white;text-align:center;">
                                            基本機能は、「認知機能」「身体機能」「口腔機能」「生活機能」です。
                                            </h4>
                                            </div>
                                            </br>"""
        st.markdown(html_temp_home1, unsafe_allow_html=True)
        st.write("""
                 To be announced
                 """)
    elif choice == "身体機能：表情検出":
        st.header("ライブ")
        st.write("笑顔を作って、「Happy」が表示されれば合格です！")
        webrtc_streamer(key="example", mode=WebRtcMode.SENDRECV, rtc_configuration=RTC_CONFIGURATION,
                        video_processor_factory=Faceemotion)

    else:
        pass


if __name__ == "__main__":
    main()
