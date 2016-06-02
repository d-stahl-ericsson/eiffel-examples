import json
import uuid
import time
import getopt
import sys
import random

def generateGenericMeta(type, t, v):
  return {'type': type, 'id': str(uuid.uuid1()), 'time': t, 'domainId': 'example.domain', 'version': v}

def link(source, target, name):
  if not target:
    return
  
  source['links'][name] = target['meta']['id']  

def linka(source, target, name):
  if not target:
    return
    
  if not name in source['links']:
    source['links'][name] = []
    
  source['links'][name].append(target['meta']['id'])
  
def generateGenericMessage(type, t, v, name, iteration):
  meta = generateGenericMeta(type, t, v)
  data = {'optionalParameters': [{'name': 'name', 'value': name}, {'name': 'iteration', 'value': iteration}]}
  links = {}
  msg = {}
  msg['meta'] = meta
  msg['data'] = data
  msg['links'] = links
  return msg
  
def findLatestPrevious(iterationsMap, currentIteration, name):
  for it in range(currentIteration - 1, -1, -1):
    if it in iterationsMap:
      if name in iterationsMap[it]:
        return iterationsMap[it][name]
  
def generateEDef1(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelEnvironmentDefinedEvent', t, '1.0', 'EDef1', iteration)
  return msg
  
def generateCDef1(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelCompositionDefinedEvent', t, '1.0', 'CDef1', iteration)
  linka(msg, findLatestPrevious(iterationsMap, iteration, 'CDef1'), 'previousVersions')
  return msg
  
def generateArtC1(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelArtifactCreatedEvent', t, '1.0', 'ArtC1', iteration)
  link(msg, iterationsMap[iteration]['CDef1'], 'composition')
  link(msg, iterationsMap[0]['EDef1'], 'environment')
  linka(msg, iterationsMap[iteration]['CDef1'], 'causes')
  linka(msg, findLatestPrevious(iterationsMap, iteration, 'ArtC1'), 'previousVersions')
  msg['data']['gav'] = {'groupId': 'com.mycompany.myproduct', 'artifactId': 'artifact-name', 'version': '1.0.0'}
  msg['data']['fileInformation'] = [{'classifier': '', 'extension': 'jar'}]
  return msg
  
def generateArtP1(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelArtifactPublishedEvent', t, '1.0', 'ArtP1', iteration)
  link(msg, iterationsMap[iteration]['ArtC1'], 'artifact')
  linka(msg, iterationsMap[iteration]['ArtC1'], 'causes')
  msg['data']['locations'] =  [{'type': 'PLAIN', 'uri': 'https://myrepository.com/myArtifact'}]
  return msg
  
def generateActT1(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelActivityTriggeredEvent', t, '1.0', 'ActT1', iteration)
  linka(msg, iterationsMap[iteration]['ArtP1'], 'causes')
  msg['data']['name'] = 'Act1'
  msg['data']['category'] = 'Test Activity'
  msg['data']['triggers'] = [{'type': 'EIFFEL_EVENT'}],
  msg['data']['executionType'] = 'AUTOMATED'
  return msg
  
def generateActS1(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelActivityStartedEvent', t, '1.0', 'ActS1', iteration)
  link(msg, iterationsMap[iteration]['ActT1'], 'activityExecution')
  return msg
  
def generateActF1(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelActivityFinishedEvent', t, '1.0', 'ActF1', iteration)
  link(msg, iterationsMap[iteration]['ActT1'], 'activityExecution')
  msg['data']['outcome'] = {'conclusion': random.choice(['SUCCESSFUL', 'UNSUCCESSFUL'])}
  return msg
  
def generateActT2(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelActivityTriggeredEvent', t, '1.0', 'ActT2', iteration)
  linka(msg, iterationsMap[iteration]['ArtP1'], 'causes')
  msg['data']['name'] = 'Act2'
  msg['data']['category'] = 'Test Activity'
  msg['data']['triggers'] = [{'type': 'EIFFEL_EVENT'}],
  msg['data']['executionType'] = 'AUTOMATED'
  return msg
  
def generateActS2(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelActivityStartedEvent', t, '1.0', 'ActS2', iteration)
  link(msg, iterationsMap[iteration]['ActT2'], 'activityExecution')
  return msg
  
def generateActF2(iterationsMap, iteration, t):
  msg = generateGenericMessage('EiffelActivityFinishedEvent', t, '1.0', 'ActF2', iteration)
  link(msg, iterationsMap[iteration]['ActT2'], 'activityExecution')
  msg['data']['outcome'] = {'conclusion': 'SUCCESSFUL'}
  return msg
  
def buildMsgArrayFromiterationsMap(iterationsMap):
  globalArray = []
  for key, itMap in iterationsMap.items():
    if itMap:
      globalArray.extend(buildMsgArrayFromIterationMap(itMap))

  return globalArray
  
def buildMsgArrayFromIterationMap(iterationMap):
  msgArray = []
  for msg in iterationMap.values():
    msgArray.append(msg)
    
  return msgArray
  
def generateIterationZeroMessages(iterationsMap, t):
  iterationsMap[0] = {}
  iterationsMap[0]['EDef1'] = generateEDef1(iterationsMap, 0, t)
  
def generateIterationMessages(iterationsMap, iteration, t):
  iterationsMap[iteration] = {}
  iterationsMap[iteration]['CDef1'] = generateCDef1(iterationsMap, iteration, t)
  t += 1000
  iterationsMap[iteration]['ArtC1'] = generateArtC1(iterationsMap, iteration, t)
  t += 1000
  iterationsMap[iteration]['ArtP1'] = generateArtP1(iterationsMap, iteration, t)
  t += 1000
  iterationsMap[iteration]['ActT1'] = generateActT1(iterationsMap, iteration, t)
  t += 2
  iterationsMap[iteration]['ActS1'] = generateActS1(iterationsMap, iteration, t)
  t += 50
  iterationsMap[iteration]['ActT2'] = generateActT2(iterationsMap, iteration, t)
  t += 5000
  iterationsMap[iteration]['ActF1'] = generateActF1(iterationsMap, iteration, t)
  t += 100000
  iterationsMap[iteration]['ActS2'] = generateActS2(iterationsMap, iteration, t)
  t += 50000
  iterationsMap[iteration]['ActF2'] = generateActF2(iterationsMap, iteration, t)
  
def main(iterations):
  t = int(time.time() * 1000)
  iterationsMap = {}
  generateIterationZeroMessages(iterationsMap, t)
  for iteration in range(1, iterations + 1):
    t += 10000
    generateIterationMessages(iterationsMap, iteration, t)

  out = buildMsgArrayFromiterationsMap(iterationsMap)

  print(json.dumps(out, indent=2, separators=(',', ': ')))
  
def usage():
  print('-h, --help')
  print('    Print this text.')
  print('-i ..., --iterations=...')
  print('    Specify the number of iterations to create.')
  print('    Default: 1')
  
try:                                
  opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "iterations="])
except getopt.GetoptError:
  usage()
  sys.exit(2)

iterations = 1  
  
for opt, arg in opts:
  if opt in ('-h', '--help'):
    usage()
    sys.exit()
  elif opt in ('-i', '--iterations'):
    iterations = int(arg)
    
main(iterations)