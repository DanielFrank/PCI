from math import sqrt
from PIL import Image,ImageDraw

def readfile(filename):
    lines=[line for line in file(filename)]
    
    #First line is the column titles
    colnames=lines[0].strip().split('\t')[1:]
    rownames=[]
    data=[]
    for line in lines[1:]:
        p=line.strip().split('\t')
        #First column in each line is the rowname
        rownames.append(p[0])
        #The data for this row is the remainder of the row
        data.append([float(x) for x in p[1:]])
    return rownames,colnames,data    

def pearson(v1,v2):
    #simple sums
    sum1=sum(v1)
    sum2=sum(v2)
    
    #Sum of the squares
    sum1Sq = sum([pow(v,2) for v in v1])
    sum2Sq = sum([pow(v,2) for v in v2])
    
    #Sum of the products
    pSum = sum([v1[i]*v2[i] for i in range(len(v1))])
    
    #Calc Pearson score
    num = pSum-(sum1*sum2/len(v1))
    den = sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den==0: return 0   
    return 1.0*num/den

class bicluster:
    def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
        self.left=left
        self.right=right
        self.vec=vec
        self.id=id
        self.distance=distance

def hcluster(rows,distance=pearson):
    distances={}
    currentclustid=-1
    
    #Clusters are initially just the rows
    clust=[bicluster(rows[i],id=i) for i in range(len(rows))]
    while len(clust) > 1:
        lowestpair=(0,1)
        closest=distance(clust[0].vec,clust[1].vec)
        
        #loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                #distances is the cache of distance calculations
                if(clust[i].id,clust[j].id) not in distances:
                    distances[(clust[i].id,clust[j].id)]=distance(clust[i].vec,clust[j].vec)
                    
                d=distances[(clust[i].id,clust[j].id)]
                if d<closest:
                    closest=d
                    lowestpair=(i,j)
        
        #Calc the average of the two clusters
        mergevec=[
            (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0
            for i in range(len(clust[lowestpair[0]].vec))]
        newcluster=bicluster(mergevec,left=clust[lowestpair[0]],right=clust[lowestpair[1]],distance=closest,id=currentclustid)
        
        #cluster ids that weren't in the original set are negative
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]

def printclust(clust,labels=None,n=0):
    #indent to make a hiearchy layout
    for i in range(n): print ' ',
    if clust.id<0:
        #megative id means it's a branch
        print '-'
    else:
        #positive id means an endpoint
        if labels==None: print clust.id
        else: print labels[clust.id]
    
    #Now print the right and left branches
    if clust.left != None: printclust(clust.left,labels=labels,n=n+1)
    if clust.right != None: printclust(clust.right,labels=labels,n=n+1)
    
def getheight(clust):
    #Is this an endpoint? Then the height is just 1
    if clust.left==None and clust.right==None: return 1
    
    #otherwise the height is the sum of the heights of each branches
    return getheight(clust.left)+getheight(clust.right)

def getdepth(clust):
    #Depth of an endpoint is 0.0
    if clust.left==None and clust.right==None: return 0.0
    
    #otherwise the depth of a branch is the greater of the depths of its sides plus its own distance
    return max(getdepth(clust.left),getdepth(clust.right)) + clust.distance

def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
    #height and width
    h= getheight(clust)*20
    w=1200
    depth=getdepth(clust)
    
    #width is fixed so scale distances accordingly
    scaling=float(w-150)/depth
    
    #Create a new image with a white background
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)

    draw.line((0,h/2,10,h/2),fill=(255,0,0))
    
    #Draw the first node
    drawnode(draw,clust,10,(h/2),scaling,labels)
    img.save(jpeg,'JPEG')
    
def drawnode(draw,clust,x,y,scaling,labels):
    if clust.id<0:
        h1=getheight(clust.left)*20
        h2=getheight(clust.right)*20
        top=y-(h1+h2)/2
        bottom=y+(h1+h2)/2
        #line length
        ll=clust.distance*scaling
        #Vertical line from this cluster to children
        draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))

        #Hroizontal line to left item
        draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))

        #Hroizontal line to right item
        draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))

        #Call the function to draw the left and right nodes
        drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
        drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
    else:
        #If this is an endpoint, draw the item label
        draw.text((x+5,y-7),labels[clust.id],(0,0,0))

def rotatematrix(data):
    newdata=[]
    for i in range(len(data[0])):
        newrow=[data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata
