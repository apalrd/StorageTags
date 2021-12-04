#Generate a single tag image for StorageTags, to print
import cv2
import numpy as np
import sys
import getopt
import random


def printHelp():
    print('Usage:')
    print('STGenTag.py -f <family> -o <output> -i <id> -d -r <factor')
    print("Family is one of:")
    for tag in TagFamilies.keys():
        print("    ",tag)
    print("Output is a file name to write")
    print('ID is a tag number valid for the family, or randomly selected if not provided')
    print('Display is optional, and will show the tag after generating it')
    print('Resize is optional, will resample the image by the integer multiple specified')
    exit(2)

#Table of pixel widths of each tag family
#This is the 'stride' in the mosaic image, +1 for the gap
#It includes the mandated white border as well
TagFamilies = {
    'tag16h5': {'stride':8,'count':30},
    'tag26h9': {'stride':9,'count':35},
    'tag36h11': {'stride':10,'count':587},
    'tagCircle21h7': {'stride':9,'count':38},
    'tagCircle49h12': {'stride':11,'count':65698},
    'tagCustom48h12': {'stride':10,'count':42211},
    'tagStandard41h12': {'stride':9,'count':2115},
    'tagStandard52h13': {'stride':10,'count':48714},
}

#Process arguments
fname = None
selected = None
outfile = None
display = False
rescale = 1
try:
    opts, args = getopt.getopt(sys.argv[1:],"f:o:i:dr:",["family=","output=","id=","display","resize="])
except getopt.GetoptError:
    printHelp()
for opt,arg in opts:
    if opt in ("-f","--family"):
        fname = arg
    elif opt in ("-o","--output"):
        outfile = arg
    elif opt in ("-i","--id"):
        print('ID arg is',arg)
        selected = int(arg)
    elif opt in ("-d","--display"):
        display = True
    elif opt in ("-r","--resize"):
        rescale = int(arg)

if fname is None:
    print("Family name not provided!")
    printHelp()
if outfile is None:
    print("Output name not selected")
    printHelp()

print("Tag Family is",fname)
print('ID is',selected)

#Check if it's within the list
if(fname not in TagFamilies):
    print("Invalid tag family:",fname)
    printHelp()
else:
    print("Tag family is valid, stride is",TagFamilies[fname]['stride'],"count is",TagFamilies[fname]['count'])

#Check to see if there's a second argument specifying the exact number
if selected is None:
    #Generate a random number for the tag ID, which start at zero
    rmax = TagFamilies[fname]['count']-1
    selected = random.randrange(0,rmax)
    print("Randomly selected tag has ID",selected)
else:
    print("User selected tag ID",selected)

#Ensure tag ID is valid
if selected >= TagFamilies[fname]['count']:
    print("Tag selected out of range. Maximum for this tag family is",TagFamilies[fname]['count']-1)
    printHelp()


# Import image
mosaic = cv2.imread("./static/"+fname+".png")
shape = mosaic.shape
print("Image shape is",shape)

#Number of tags per row / col
npix = TagFamilies[fname]['stride']+1
nrow = int((shape[0]+1)/npix)
ncol = int((shape[1]+1)/npix)
print("Rows",nrow,"Columns",ncol)

#Find the row and column the random ID is in
#Note that both row and col are 0-indexed
frow = selected / (nrow-1)
row = int(frow)
frac = frow - row
col = int(frac * ncol)
print("Selected is row",row,"float",frow,"frac",frac,"col",col)

#Snip out the pixels in the immediate area at the correct index
width = TagFamilies[fname]['stride']
stride = width + 1
roff = row * stride
coff = col * stride
print("Roff",roff,"Coff",coff)
subset = mosaic[roff:(roff+width),coff:(coff+width)]

#Write file
print("Rescale by factor of",rescale)
output = cv2.resize(subset,(width*rescale,width*rescale),interpolation=cv2.INTER_NEAREST)
cv2.imwrite(outfile,output)

#Display image
if display:
    newsize = (width*24,width*24)
    print("Newsize",newsize)
    subsetBig = cv2.resize(subset,newsize,interpolation=cv2.INTER_NEAREST)
    cv2.imshow("Subset",subsetBig)
    cv2.waitKey(0)
    cv2.destroyAllWindows()