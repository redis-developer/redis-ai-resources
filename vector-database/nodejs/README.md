# Redis VSS + AI Examples in Nodejs

## Contents
1.  [Summary](#summary)
2.  [Architecture](#architecture)
3.  [Features](#features)
4.  [Prerequisites](#prerequisites)
5.  [Installation](#installation)
6.  [Usage](#usage)
7.  [Execution](#execution)

## Summary <a name="summary"></a>
This provides a series of examples of how to use Redis VSS in a Nodejs domain.  Both standalone vector searches and
searches in conjunction with AI queries are demonstrated.

## Architecture <a name="architecture"></a>
![architecture](https://docs.google.com/drawings/d/e/2PACX-1vQlOwYbS5EN29m1Ld2lbZQA16oiB4h1T_x8q0N9_pi8pYNiDQw9igTsP9IZVm1Zje_FQvgag9GJqlaW/pub?w=462&h=268)


## Features <a name="features"></a>
- Nodejs source for implementing Redis VSS on hash sets and JSON
- Nodejs source for creating a OpenAI client and executing ChatCompletion and Embedding operations
- Docker compose file to start up a Redis Stack instance.

## Prerequisites <a name="prerequisites"></a>
- Docker
- Nodejs
- OpenAI key

## Installation <a name="installation"></a>
1.  Clone this repo.
2.  CD to the nodejs directory
3.  Create a .env file and add this line:  OPENAI_API_KEY="your key"
4.  Start up Redis Stack:  docker compose up -d
5.  Execute the node app:  npm start

## Execution <a name="execution"></a>
### Redis Client Connection 
 ```text
PONG
 ```
 ### OpenAI Client Connection
 ```text
Pong!
 ```
 ### Index Build
 ```text
idx1 (FLAT, L2, 1536, FLOAT32, JSON): OK
idx2 (HNSW, COSINE, 1536, FLOAT32, M=48, HASH): OK
 ```
### Data Load
```text
Number of JSON documents loaded: 10
Number of HASH documents loaded: 10
```
### Vector Search Scenario #1
```text
Scenario:  JSON docs, FLAT index, Top 2 KNN, Sports topic input

key: jsonDoc:6
content: O'Sullivan commits to Dublin race  Sonia O'Sullivan will seek to regain her title at the Bupa Great Ireland Run on 9 April in Dublin.  The 35-year-old was beaten into fourth at last year's event, having won it a year earlier. "I understand she's had a solid winter's training down in Australia after recovering from a minor injury," said race director Matthew Turnbull. Mark Carroll, Irish record holder at 3km, 5km and 10km, will make his debut in the mass participation 10km race. Carroll has stepped up his form in recent weeks and in late January scored an impressive 3,000m victory over leading American Alan Webb in Boston. Carroll will be facing stiff competition from Australian Craig Mottram, winner in Dublin for the last two years. 

key: jsonDoc:7
content: Hansen 'delays return until 2006'  British triple jumper Ashia Hansen has ruled out a comeback this year after a setback in her recovery from a bad knee injury, according to reports.  Hansen, the Commonwealth and European champion, has been sidelined since the European Cup in Poland in June 2004. It was hoped she would be able to return this summer, but the wound from the injury has been very slow to heal. Her coach Aston Moore told the Times: "We're not looking at any sooner than 2006, not as a triple jumper." Moore said Hansen may be able to return to sprinting and long jumping sooner, but there is no short-term prospect of her being involved again in her specialist event. "There was a problem with the wound healing and it set back her rehabilitation by about two months, but that has been solved and we can push ahead now," he said. "The aim is for her to get fit as an athlete - then we will start looking at sprinting and the long jump as an introduction back to the competitive arena." Moore said he is confident Hansen can make it back to top-level competition, though it is unclear if that will be in time for the Commonwealth Games in Melbourne next March, when she will be 34. "It's been a frustrating time for her, but it has not fazed her determination," he added. 
```
### Vector Search Scenario #2
```text
Scenario:  HASH docs, HNSW index, Hybrid w/Top 2 KNN, Entertainment topic input

key: hashDoc:3
content: Slater to star in Broadway play  Actor Christian Slater is stepping into the role of Tom in the Broadway revival of The Glass Menagerie.  Slater, 35, is replacing actor Dallas Roberts in the Tennessee Williams drama, which opens next month. No reason was given for Roberts' departure. The role will be played by understudy Joey Collins until Slater joins the show. Slater won rave reviews for his recent performance in One Flew Over the Cuckoo's Nest in London's West End.  He has also starred in a number of films, including Heathers, Robin Hood: Prince of Thieves and more recently Churchill: The Hollywood Years. Preview performances of The Glass Menagerie will begin at New York's Ethel Barrymore Theatre on Thursday. Philip Rinaldi, a spokesman for the show, said the play's 15 March opening date remains unchanged. The revival, directed by David Leveaux, will also star Jessica Lange as the domineering mother, Amanda Wingfield.
```
### AI Q&A Scenario #1
```text
Scenario:  Ask the AI a question which is outside of its knowledge base
Prompt: Is Sam Bankman-Fried's company, FTX, considered a well-managed company?

Response: As an AI language model, I cannot provide a personal opinion. However, FTX has been recognized as one of the fastest-growing cryptocurrency exchanges and has received positive reviews for its user-friendly interface, low fees, and innovative products. Additionally, Sam Bankman-Fried has been praised for his leadership and strategic decision-making, including FTX's recent acquisition of Blockfolio. Overall, FTX appears to be a well-managed company.
```
### AI Q&A Scenario #2
```text
Scenario:  Vectorize the question, search Redis for relevant docs, then provide additional info from Redis to the AI
Prompt: Using the information delimited by triple hyphens, answer this question: Is Sam Bankman-Fried's company, FTX, considered a well-managed company?

    Context: ---Embattled Crypto Exchange FTX Files for Bankruptcy  Nov. 11, 2022 On Monday, Sam Bankman-Fried, the chief executive of the cryptocurrency exchange FTX, took to Twitter to reassure his customers: “FTX is fine,” he wrote. “Assets are fine.”  On Friday, FTX announced that it was filing for bankruptcy, capping an extraordinary week of corporate drama that has upended crypto markets, sent shock waves through an industry struggling to gain mainstream credibility and sparked government investigations that could lead to more damaging revelations or even criminal charges.  In a statement on Twitter, the company said that Mr. Bankman-Fried had resigned, with John J. Ray III, a corporate turnaround specialist, taking over as chief executive.  The speed of FTX’s downfall has left crypto insiders stunned. Just days ago, Mr. Bankman-Fried was considered one of the smartest leaders in the crypto industry, an influential figure in Washington who was lobbying to shape regulations. (abbreviated) ---

Response: No, FTX is not considered a well-managed company as it has filed for bankruptcy and owes as much as $8 billion to its creditors. The collapse of FTX has also destabilized the crypto industry and sparked government investigations into the company's practices. The bankruptcy filing included FTX, its U.S. arm, and Alameda Research, a trading firm that Mr. Bankman-Fried also founded, and has left investors and customers scrambling to salvage funds. The bankruptcy is a stunning fall from grace for Mr. Bankman-Fried, who was considered one of the smartest leaders in the crypto industry and an influential figure in Washington.
```