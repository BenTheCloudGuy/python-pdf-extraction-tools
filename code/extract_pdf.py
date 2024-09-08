import PyPDF2
import fitz
import os
import re
import requests

# Function to extract text from pdf
def pdf_to_text(file_path, output_txt_path):
    # Open the PDF file in read-binary mode
    with open(file_path, 'rb') as file:
        # Initialize a PDF reader object
        reader = PyPDF2.PdfReader(file)
        
        # Extract text from each page
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Write the extracted text to a .txt file
    outputFile = os.path.join(output_txt_path, 'output.txt')
    with open(outputFile, 'w', encoding='utf-8') as text_file:
        text_file.write(text)

# Function to extract images from pdf
def extract_images_from_pdf(pdf_path, output_dir):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    image_count = 0
    # Iterate through each page
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        images = page.get_images(full=True)

        # Iterate through the images on each page
        for image_index, img in enumerate(images):
            # Extract the image
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Define image output path
            image_output_path = os.path.join(output_dir, f"image_page_{page_number+1}_{image_index+1}.{image_ext}")

            # Write image to file
            with open(image_output_path, "wb") as image_file:
                image_file.write(image_bytes)

            # Upscale the Image
            upscale_images(output_dir,image_output_path)

            image_count += 1

    return image_count

# Upscale Images Extracted from PDF
def upscale_images(output_dir,image_output_path):
 
    # Uri and API Key
    url = "https://api.claid.ai/v1-beta1/image/edit/upload"
    apiKey = "YOUR_API_KEY"
    upscaledImageName = image_output_path.split('/')[-1]

    # Create folder for upscaled images
    if not os.path.exists(f'{output_dir}/upscaled_images'):
        os.makedirs(f'{output_dir}/upscaled_images')

    # Set resize percentage
    resize_percentage = '200%'

    headers = {
        "Host": url,
        "Authorization": f'Bearer {apiKey}',
        "Content-Type": "multipart/form-data"
    }

    files = {
        'file': (upscaledImageName, open(image_output_path, 'rb')),
        'data': (None, '{"operations":{"resizing":{"width":200%},"background":{"remove":false}}}', 'application/json')
    }




# Get the path to the output directory and create if does not exist
output_directory = input("Enter the path to the output directory: ")
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


# Get the path to the source directory and exit if does not exit or add files to fileList array
src_directory = "./src"
if not os.path.exists(src_directory):
    print("The output directory does not exist. Please create and populate with src PDFs.")
    exit()
else:
    # Get the list of PDF files in the source directory
    fileList = []
    for file in os.listdir(src_directory):
        if file.endswith(".pdf"):
            fileList.append(file)              
    print(f'Found the following Files: {fileList}')


# Validate there are PDFs in the Directory. 
if len(fileList) == 0:
    print("The source directory is empty. Please populate with src PDFs.")
    exit()

# If there are PDFS, lets do some work..
else:
    # Iterate through the list of PDF files and do 'things' to them
    for pdf_file in fileList:
        # Create srcFilePath by joining the src_directory and pdf_file
        srcfilePath = os.path.join(src_directory,pdf_file)
        # Create outputPath and make the directory if not exist by joining the output_directory and pdf_file stripped of special character
        outputPath = os.path.join(output_directory,re.sub('[^A-Za-z0-9]+', '', pdf_file))
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        # Extract text from the PDF by calling pdf_to_text function
        pdf_to_text(srcfilePath,outputPath)

        # Extract images from the PDF by calling extract_images_from_pdf function
        imgage_count = extract_images_from_pdf(srcfilePath,outputPath)

        print(f'Extracting text and images {imgage_count} from {srcfilePath} to {outputPath}.')



