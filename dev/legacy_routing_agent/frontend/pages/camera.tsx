import { useRef, useState } from "react";
import {Camera} from "react-camera-pro";

export default function MainCamera() {
  const camera = useRef(null);
  const [image, setImage] = useState(null);
  
  return (
  <div className="flex flex-col lg:justify-around items-center h-[50rem]">
    <div className="flex self-center h-[60%] w-[80%] m-4 lg:h-[30%] lg:w-[40%]">
      <Camera 
        ref={camera} 
        facingMode='environment'
        aspectRatio={16/9} 
        errorMessages={
          {
            noCameraAccessible: 'no camera accessible',
            permissionDenied: 'permission denied',
            switchCamera: 'switch cameras',
            canvas: 'canvas',
          }
        } 
      />
    </div>
    <div className="flex flex-row mb-8">
      <button
        className="w-14 h-4 bg-white text-black m-4 text-sm	"
        onClick={() => {
          //@ts-ignore
          camera.current.switchCamera();
        }}
      >
        Switch Camera
      </button>
      <button onClick={
        () => {
          //@ts-ignore
          setImage(camera.current.takePhoto());
          console.log("photo taken");
          console.log(image);
        }
      }>
        Take photo
      </button>      
    </div>
    {image && 
      <div>
        <h1> 
          Using Photo:
        </h1>
        <img
          width={200}
          height={200}
          src={image}
        />
      </div>
    }
  </div>
  )
};