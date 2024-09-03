
from Functions import *
import requests
import aiohttp
import asyncio


# source = './TestingVideos/FT1.mov' 

# constants
save_video = True
show_video= False 
save_img=False  

image_counter = []


async def biker_safety_detection (source) : 
   
	#saveing video as output
	# fourcc = cv2.VideoWriter_fourcc(*'avc1')
	fourcc = cv2.VideoWriter_fourcc(*'H264')
	# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	# out = cv2.VideoWriter('output.mp4', fourcc, 20.0, frame_size)
	# out = cv2.VideoWriter('/BSD-FE/src/assets/videos/output.mp4', fourcc, 20.0, frame_size)
	out = cv2.VideoWriter('BSD-FE/src/assets/videos/output.mp4', fourcc, 20.0, frame_size)
	# out = cv2.VideoWriter('output.mp4', fourcc, 20.0, frame_size)
 


	best_propability = 0
	best_propability_number = 0
	response = {
		"VideoURL": "",
		"Images": []
	}

	cap = cv2.VideoCapture(source)
	while(cap.isOpened()):
		ret, frame = cap.read()
		if ret == True:
			frame = cv2.resize(frame, frame_size)  
			orifinal_frame = frame.copy()
			frame, results = object_detection(frame) 

			rider_list = []
			head_list = []
			number_list = []

			for result in results:
				x1,y1,x2,y2,cnf, clas = result
				if clas == 0:
					rider_list.append(result)
				elif clas == 1:
					head_list.append(result)
				elif clas == 2:
					number_list.append(result)

			for rdr in rider_list:
				time_stamp = str(time.time())
				x1r, y1r, x2r, y2r, cnfr, clasr = rdr
				for hd in head_list:
					x1h, y1h, x2h, y2h, cnfh, clash = hd
					if inside_box([x1r,y1r,x2r,y2r], [x1h,y1h,x2h,y2h]): 
						try:
							head_img = orifinal_frame[y1h:y2h, x1h:x2h]
							helmet_present = img_classify(head_img)
						except:
							helmet_present[0] = None

						if  helmet_present[0] == True: # helmet present
							frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0,255,0), 1)
							frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
						elif helmet_present[0] == None: # Poor prediction
							frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 255, 255), 1)
							frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
						elif helmet_present[0] == False: # helmet absent 
							frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 0, 255), 1)
							frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
							try:
								if helmet_present[1] > best_propability: 
									best_propability = helmet_present[1]
									cv2.imwrite(f'BSD-FE/src/assets/images/RiderImage_{time_stamp}.jpg', frame)
									link = await UploadFile(f"BSD-FE/src/assets/images/RiderImage_{time_stamp}.jpg")
									response['Images'].append(link)
         
							except:
								print('could not save rider')

							for num in number_list:
								x1_num, y1_num, x2_num, y2_num, conf_num, clas_num = num
								if inside_box([x1r,y1r,x2r,y2r], [x1_num, y1_num, x2_num, y2_num]):
									try:									
										if conf_num > best_propability_number:
											best_propability_number = conf_num
											num_img = orifinal_frame
											cv2.imwrite(f'BSD-FE/src/assets/images/NumberPlate_{time_stamp}.jpg', num_img)
											link = await UploadFile(f"BSD-FE/src/assets/images/NumberPlate_{time_stamp}.jpg")
											response['Images'].append(link)
									except:
										print('could not save number plate')
										
			if save_video: 
				out.write(frame)
			if save_img: #save img
				cv2.imwrite('saved_frame.jpg', frame)
			if show_video: # show video
				frame = cv2.resize(frame, (900, 450))
				cv2.imshow('Frame', frame)


			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
				
		else:
			break

	cap.release()
	cv2.destroyAllWindows()
 
	link = await UploadFile("BSD-FE/src/assets/videos/output.mp4")
	response['VideoURL'] = link
	return response
	print('Execution completed')


async def UploadFile(file_path):
    url = 'https://api.streamable.com/upload'
    
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as file:
                async with session.post(url, data={'file': file}) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("Upload successful!")
                        print("Download link:", data.get('url'))
                        link = data.get('url')
                        return link
                    else:
                        print("Failed to upload file:", await response.text())
                        return None
    except FileNotFoundError:
        print("File not found:", file_path)
    except aiohttp.ClientError as e:
        print("Request failed:", e)