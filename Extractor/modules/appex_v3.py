import json
import os
import requests
import threading
import asyncio
from pyrogram import filters
from pyrogram.types import Message
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import config
from Extractor import app

def decrypt_data(encoded_data):
    try:
        key = "638udh3829162018".encode("utf8")
        iv = "fedcba9876543210".encode("utf8")
        decoded_data = b64decode(encoded_data)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(decoded_data), AES.block_size)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""

async def appex_down(app, message, hdr1, api, raw_text2, fuk, batch_name, name, prog):
    vt = ""
    try:
        subject_ids = fuk.split('&')
        for subject_id in subject_ids:
            if not subject_id:
                continue

            # Get all topics for the current subject
            res3 = requests.get(f"https://{api}/get/alltopicfrmlivecourseclass?courseid={raw_text2}&subjectid={subject_id}", headers=hdr1)
            topics = res3.json().get('data', [])
            vj = ""
            
            for topic in topics:
                topic_id = topic.get("topicid")
                if not topic_id:
                    continue

                # Get all materials for the current topic
                res4 = requests.get(f"https://{api}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={topic_id}&start=-1&courseid={raw_text2}&subjectid={subject_id}", headers=hdr1).json()
                materials = res4.get("data", [])

                for material in materials:
                    title = material.get("Title", "No Title")
                    material_type = material.get('material_type')
                    video_link = ""
                    pdf_link = ""

                    # Handle Video Material
                    if material_type == 'VIDEO':
                        if material.get('ytFlag') == 0 and material.get('ytFlagWeb') == 0:
                            # Attempt to get direct video download link
                            dlink = next((link['path'] for link in material.get('download_links', []) if link.get('quality') == "720p"), None)
                            if dlink:
                                parts = dlink.split(':')
                                if len(parts) == 2:
                                    encoded_part, encrypted_part = parts
                                    video_link = decrypt_data(encoded_part)
                            else:
                                print(f"No download link found for video {title}")

                        elif material.get('ytFlag') == 1:
                            # YouTube link handling
                            dlink = material.get('file_link')
                            if dlink:
                                encoded_part, encrypted_part = dlink.split(':')
                                video_id = decrypt_data(encoded_part).split('/')[-1]
                                video_link = f"https://youtu.be/{video_id}"
                            else:
                                print(f"No YouTube link found for video {title}")

                        vj += f"{title} : {video_link}\n"

                    # Handle PDF Material
                    elif material_type == 'PDF':
                        plink = material.get("pdf_link", "").split(':')
                        if len(plink) == 2:
                            encoded_part, encrypted_part = plink
                            pdf_link = decrypt_data(encoded_part)
                        vj += f"{title} : {pdf_link}\n"

            vt += vj

        # Save data to file
        mm = batch_name
        cap = f"**App Name :- {name}\nBatch Name :-** `{batch_name}`"
        with open(f'{mm}.txt', 'a') as f:
            f.write(f"{vt}")
        await app.send_document(message.chat.id, document=f"{mm}.txt", caption=cap)
        await prog.delete()
        file_path = f"{mm}.txt"
        os.remove(file_path)
        await message.reply_text("Done")
    except Exception as e:
        print(str(e))
        await message.reply_text("An error occurred. Please try again later.")

async def appex_v3_txt(app, message, api, name):
    global cancel
    cancel = False
    token = ""
    
    input1 = await app.ask(message.chat.id, text="Send **Token**. If you don’t have one, type `NO` to login with ID & Password.")
    token_text = input1.text

    if token_text.strip().upper() != "NO":
        token = token_text
    else:
        # Prompt for ID and Password if Token is not provided
        raw_url = f"https://{api}/post/userLogin"
        hdr = {
            "Auth-Key": "appxapi",
            "User-Id": "-2",
            "Authorization": "",
            "User_app_category": "",
            "Language": "en",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "okhttp/4.9.1"
        }
        info = {"email": "", "password": ""}
        input2 = await app.ask(message.chat.id, text="Send **ID & Password** in this manner, otherwise, the bot will not respond.\n\nSend like this: **ID*Password**")
        raw_text = input2.text
        info["email"] = raw_text.split("*")[0]
        info["password"] = raw_text.split("*")[1]
        await input2.delete(True)

        scraper = cloudscraper.create_scraper()
        res = scraper.post(raw_url, data=info, headers=hdr).content
        output = json.loads(res)
        token = output["data"]["token"]

    # Use token to retrieve course data
    await message.reply_text("**Login Successful**")
    hdr1 = {
        "Host": api,
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": token if token else "-2",
        "Authorization": token
    }
    res1 = requests.get(f"https://{api}/get/mycourseweb?userid={token}", headers=hdr1)
    b_data = res1.json()['data']
    
    # Display available batches
    cool = ""
    for data in b_data:
        t_name = data['course_name']
        FFF = "BATCH-ID - BATCH NAME - INSTRUCTOR"
        aa = f"**`{data['id']}`      - `{data['course_name']}`**\n\n"
        if len(f'{cool}{aa}') > 4096:
            print(aa)
            cool = ""
        cool += aa
    await message.reply_text(f"**YOU HAVE THESE BATCHES:**\n\n{FFF}\n\n{cool}")
    
    # Ask for Batch ID to download
    input3 = await app.ask(message.chat.id, text="**Now send the Batch ID to Download**")
    raw_text2 = input3.text
    for data in b_data:
        if data['id'] == raw_text2:
            batch_name = data['course_name']
    
    # Get subjects in the selected batch
    scraper = cloudscraper.create_scraper()
    html = scraper.get(f"https://{api}/get/allsubjectfrmlivecourseclass?courseid={raw_text2}", headers=hdr1).content
    output0 = json.loads(html)
    subjID = output0["data"]
    
    # Build subject IDs list
    fuk = "&".join([sub["subjectid"] for sub in subjID if "subjectid" in sub])

    # Begin download process
    prog = await message.reply_text("**Extracting Videos Links Please Wait  📥 **") 
    thread = threading.Thread(target=lambda: asyncio.run(appex_down(app, message, hdr1, api, raw_text2, fuk, batch_name, name, prog)))
    thread.start()
