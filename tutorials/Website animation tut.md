# How to VibeCode Beautiful Animated Websites with AntiGravity

This tutorial breaks down the process of creating stunning, animated websites from scratch without any coding experience. By chaining together free AI tools, you can build interactive websites that look highly professional.

## Tools Used
* **Google Gemini:** For image prompt generation and script adaptation.
* **Google Whisk:** An AI image generator for creating our "end state" effects.
* **Google Flow:** An AI video generator to create the animation transition between frames.
* **EZGIF:** A free online tool to convert video into individual image frames.
* **AntiGravity:** The main AI website builder to assemble the code and animations.
* **Netlify:** For free static website hosting.

---

## Step-by-Step Tutorial

### Step 1: Generate the Base Image [00:00:26]
1. Open **Google Gemini** and prompt it to generate your primary product image. 
2. *Example Prompt:* "I need an image of an iced matcha coffee cup takeaway with no lid and straw, make it realistic and super tasty."
3. Refine the output until you have exactly what you want. Ensure the subject is centered against a black background (e.g., "remove the mint on top, make the cup larger, and make the image vertical") [00:01:35].
4. Download the final base image.

### Step 2: Create the "End Frame" Effect [00:02:24]
1. You will need an "end frame script" (the video creator provides a template in their free community).
2. Go back to **Google Gemini** to adapt the generic end-frame script specifically to your generated product (e.g., "adapt this prompt to my image, please just fill blanks and don't generate any images").
3. Go to **Google Whisk**.
4. Upload your primary base image and paste in your newly adapted script [00:03:16].
5. Generate images. If the results break the core product apart, refine the prompt (e.g., "I want the coffee to stay the same, just add flying ice cubes and liquid drops from the sky") [00:04:25].
6. Once you get a highly dynamic, splashing end-result image, download it [00:06:18].

### Step 3: Animate the Transition [00:06:39]
1. Go to **Google Flow**.
2. Start a new project and select **Frame to Video**.
3. Ensure the quality settings are set to **VO3.1** (avoid "fast" settings) [00:06:56].
4. Insert your starting frame (the base image) and your end frame (the splashing image).
5. Paste in the Google Flow transition script (also provided via the creator's community) and click Generate.
6. Review the animation. If it looks good, download the **upscaled version** of the video [00:08:37].

### Step 4: Convert the Video into Image Frames [00:08:56]
1. Head over to **EZGIF** and navigate to the **Video to JPG Converter**.
2. Upload your downloaded animation video.
3. Configure the settings:
   * **Start time:** Trim any static opening frames (e.g., start at 2 seconds) [00:09:38].
   * **Frame Rate:** Increase it to 29 or 30 FPS for smooth scrolling [00:09:52].
4. Click Convert to generate the images.
5. Download the output as a ZIP folder (you should have over 100 individual frames) [00:10:22].

### Step 5: Generate the Website with AntiGravity [00:10:59]
1. Go to **Google Gemini** to adapt your website generation prompt (template from the creator's community) for your specific product and animation.
2. Open **AntiGravity**.
3. Upload your extracted image frames (the unzipped folder) into the platform [00:11:48].
4. Paste the adapted website code prompt into the prompt box.
5. Select the **Gemini 3 Pro** model and ensure it is set to **Planning** mode [00:12:07].
6. Click Generate. Wait while AntiGravity writes the code and hooks up the scroll animations.

### Step 6: Export and Host for Free [00:13:11]
1. Once the website looks good inside AntiGravity, give the AI a final prompt: *"I want to host it on Netlify as a static web, give me code."*
2. The AI will pack the files into an `out` folder [00:13:31].
3. Locate this folder on your computer.
4. Go to **Netlify** (create a free account if you don't have one).
5. Drag and drop the `out` folder directly into the Netlify Drop area [00:14:20].
6. Your animated website is now live! You can manage the domain settings in Netlify's product overview to connect a custom domain [00:14:40].