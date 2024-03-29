# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

#Returns a distance-based similarity score for person1 & person2
def sim_distance(prefs, person1,person2):
    #Get the list of shared items
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
    #if no ratings in common, return 0
    if len(si)==0: return 0
    
    #Add up the squares of all the differences
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                        for item in si])
    return 1/(1+sqrt(sum_of_squares))

#Returns the Pearson correlation coefficient for person1 & person2
def sim_pearson(prefs,p1,p2):
    #Get the list of shared items
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    
    n = len(si)
    #if no ratings in common, return 0
    if n==0: return 0
    
    #Add up all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    #Add up the suares
    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])

    #Add up the products
    pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])
    
    #Calc Pearson score
    num = pSum-(sum1*sum2/n)
    den = sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0   
    r=num/den
    return r

#Returns best matchs for person from prefs dictionary
#Number of results and similarity function are optional
def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores=[(similarity(prefs,person,other),other)
        for other in prefs if other!=person]
    #Sort the list so the highest score appears on the top
    scores.sort()
    scores.reverse()
    return scores[0:n]


#Gets recommendations for a person by using a weighted average
#of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        #Avoid comparing person to self
        if other==person: continue
        sim=similarity(prefs,person,other)
        
        #ignore scores of zero or less
        if sim<=0: continue
        for item in prefs[other]:
            
            #only score moves I haven't seen yet
            if item not in prefs[person] or prefs[person][item]==0:
                #Similarity * Score
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                #sum of similarities
                simSums.setdefault(item,0)
                simSums[item]+=sim
    rankings=[(total/simSums[item],item) for item, total in totals.items()]
    #Return sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            #Flip item and person
            result[item][person] = prefs[person][item]
    return result

#Create a dictionary of items showing which other items they are most similar to
def calculateSimilarItems(prefs,n=10):
    result={}
    
    #Invert the pref matrix to be item-centric
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        #Status update for large datasets
        c+=1
        if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        #Find the most similar items to this one
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result

#Get recommendations by taking advantage of item-based filtering
def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    
    #Loop over item rated by user
    for (item, rating) in userRatings.items():
        
        #Loop over items similar to this one
        for (similarity,item2) in itemMatch[item]:
            
            #Ignore if user rated this item
            if item2 in userRatings: continue
            
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating

            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity

    rankings=[(score/totalSim[item],item) for item, score in scores.items()]
    
    #Return sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

#Load data from movieLens
def loadMovieLens(path):
    #Get movie titles
    movies={}
    for line in open(path+'/u.item'):
        (id,title)=line.split('|')[0:2]
        movies[id]=title
    #Load data
    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]]=float(rating)
    return prefs
