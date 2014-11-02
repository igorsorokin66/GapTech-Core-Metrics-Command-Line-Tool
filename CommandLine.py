from pymongo import MongoClient

client = MongoClient()

db = client.iterations
iterationsCollection = db.iter
storiesCollection = db.story

allStoryIdsCursorType = storiesCollection.find({},{'_id':1})
allProjectsUnsorted = []
for storyId in allStoryIdsCursorType:
    allProjectsUnsorted.append(str(storyId['_id']).split("-")[0])


allProjects = []
def updateLegacyProjects():
    legacyProjects = [line.strip().upper() for line in open('legacyProjects')]
    validProjects = set(allProjectsUnsorted).difference(set(legacyProjects))
    del allProjects[:]
    allProjects.extend(list(sorted(validProjects)))
updateLegacyProjects()

def displayProjects():
    for project in allProjects:
        print(project)

allIterationsCursorType = iterationsCollection.find({},{'ITERATION':1})
allIterations = []
for iteration in allIterationsCursorType:
    allIterations.append(iteration['ITERATION'])
def displayIterations():
    for iteration in allIterations:
        print(iteration)

import re
def cycleTime(requestedIterations, requestedProjects):
    for requestedIteration in requestedIterations:
        #find_one returns a dict, using key start or end returns datetime element
        startDate = iterationsCollection.find_one({'ITERATION':requestedIteration},{'START':1,'_id':0})['START']
        endDate = iterationsCollection.find_one({'ITERATION':requestedIteration},{'END':1,'_id':0})['END']
        for requestedProject in requestedProjects:
            regexForRequestedProject = re.compile('.*'+requestedProject+'.*')
            storiesWithRequestedIterationAndRequestedProject = storiesCollection.find({'signOffDate':{'$gte': startDate,'$lte': endDate},'_id':{'$regex':regexForRequestedProject}})
            listOfAllCycleTimesForRequestedIterationAndRequestedProject = []
            for story in storiesWithRequestedIterationAndRequestedProject:
                listOfAllCycleTimesForRequestedIterationAndRequestedProject.append(story['transitions'][1]['numberOfDays'])#InProgress
                listOfAllCycleTimesForRequestedIterationAndRequestedProject.append(story['transitions'][2]['numberOfDays'])#Validation
                listOfAllCycleTimesForRequestedIterationAndRequestedProject.append(story['transitions'][3]['numberOfDays'])#Signoff
            totalCycleTimeForRequestedIterationAndRequestedProject = sum(listOfAllCycleTimesForRequestedIterationAndRequestedProject)
            if storiesWithRequestedIterationAndRequestedProject.count() == 0:
                averageCycleTimeForRequestedIterationAndRequestedProject = 0
                standardDeviation = 0
            else:
                averageCycleTimeForRequestedIterationAndRequestedProject = round(totalCycleTimeForRequestedIterationAndRequestedProject/storiesWithRequestedIterationAndRequestedProject.count(),2)
                variance = sum([(individualCycleTime - averageCycleTimeForRequestedIterationAndRequestedProject)**2 for individualCycleTime in listOfAllCycleTimesForRequestedIterationAndRequestedProject])/storiesWithRequestedIterationAndRequestedProject.count()
                standardDeviation = round(variance**(.5),2)
            print("Iteration: " + str(requestedIteration) + "\t\tProject: " + str(requestedProject) + "\t\tCycleTime: " + str(averageCycleTimeForRequestedIterationAndRequestedProject) + "\t\tStandard Deviation: " + str(standardDeviation))

print("Valid Commands:")
print("Display GID - displays all valid GID projects")
print("Display Iterations - displays all valid iterations")
print("Remove [projectName] - removes a project")
print("CycleTime [GID or projects or project] [allIterations or iterations or iteration]")
print("")
#cycletime jlo miniq mtl 260 261
while True:
    command = raw_input("Enter Command: ")
    if command.lower() == "display gid":
        displayProjects()
    if command.lower() == "display iterations":
        displayIterations()
    if command.lower().startswith("cycletime"):
        requestedProjects = []
        requestedIterations = []
        for field in command.split("cycletime")[1].split():
            if field.isdigit():
                if int(field) not in allIterations:
                    print("Invalid Iteration: " + field)
                    break
                else:
                    requestedIterations.append(int(field))
            else:
                if field.upper() == "GID":
                    requestedProjects = allProjects
                elif field.upper() == "ALLITERATIONS":
                    requestedIterations = allIterations
                else:
                    if field.upper() not in allProjects:
                        print("Invalid Project: " + field)
                        break
                    else:
                        requestedProjects.append(field.upper())
        cycleTime(requestedIterations, requestedProjects)
    if command.lower().startswith("remove"):
        f = open('legacyProjects','a')
        for legacyProject in command.split("remove")[1].split():
            f.write(legacyProject+'\n')
        f.close()
        updateLegacyProjects()
    if command.lower() == "quit":
        break