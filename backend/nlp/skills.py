"""Skill taxonomy used for rule-based extraction (lowercase canonical names)."""
CATS = {
 "language": ["python","java","javascript","typescript","c","c++","c#","go","rust","php","ruby","swift","kotlin","sql","r","matlab","scala","bash","shell scripting","html","css","dart","perl","solidity","pl/sql"],
 "web": ["react","angular","vue","svelte","node.js","express","flask","django","fastapi","spring boot","laravel","asp.net",".net","tailwind css","bootstrap","next.js","redux","jquery","sass","webpack","vite","graphql","rest api","websockets","jwt","oauth","microservices","android","ios","flutter","react native"],
 "database": ["mysql","postgresql","mongodb","sqlite","redis","firebase","oracle","sql server","dynamodb","cassandra","elasticsearch","neo4j","nosql","dbms","rdbms"],
 "cloud_devops": ["aws","azure","gcp","docker","kubernetes","terraform","ansible","jenkins","ci/cd","github actions","gitlab ci","linux","nginx","prometheus","grafana","helm","cloudformation","devops","sre","site reliability","monitoring","ec2","s3","aws lambda","load balancing","incident management"],
 "data_ml": ["machine learning","deep learning","nlp","computer vision","tensorflow","pytorch","keras","scikit-learn","pandas","numpy","scipy","spacy","nltk","opencv","mediapipe","hugging face","transformers","llm","generative ai","langchain","rag","prompt engineering","data analysis","data science","data visualization","statistics","power bi","tableau","excel","hadoop","spark","kafka","airflow","etl","data engineering","data warehousing","big data","mlops","matplotlib","seaborn","xgboost","reinforcement learning","neural networks"],
 "tools": ["git","github","gitlab","bitbucket","jira","confluence","postman","figma","selenium","junit","pytest","cypress","jest","swagger","maven","gradle","npm"],
 "concepts": ["data structures","algorithms","oop","design patterns","system design","agile","scrum","kanban","tdd","unit testing","api design","networking","operating systems","cybersecurity","software testing","automation","scripting","debugging","troubleshooting","distributed systems","multithreading","caching"],
}
LANGUAGES = CATS["language"]
ALL_SKILLS = sorted({s for v in CATS.values() for s in v})
# Short/ambiguous words: matched case-sensitively in this exact form (avoids "go to market", "excel in", ...)
AMBIG = {"c":"C","r":"R","go":"Go","swift":"Swift","rust":"Rust","ruby":"Ruby","dart":"Dart","express":"Express","excel":"Excel","spark":"Spark","node":"Node","ml":"ML","js":"JS","ts":"TS"}
ALIASES = {"js":"javascript","ts":"typescript","reactjs":"react","react.js":"react","nodejs":"node.js","node":"node.js","expressjs":"express","express.js":"express",
 "vuejs":"vue","vue.js":"vue","angularjs":"angular","postgres":"postgresql","mongo":"mongodb","ms sql":"sql server","mssql":"sql server","html5":"html","css3":"css",
 "sklearn":"scikit-learn","scikit learn":"scikit-learn","ml":"machine learning","natural language processing":"nlp","k8s":"kubernetes","golang":"go","cpp":"c++",
 "amazon web services":"aws","google cloud":"gcp","google cloud platform":"gcp","restful":"rest api","restful api":"rest api","restful apis":"rest api","rest apis":"rest api",
 "object oriented":"oop","object-oriented":"oop","object oriented programming":"oop","object-oriented programming":"oop","tailwind":"tailwind css","springboot":"spring boot","spring framework":"spring boot",
 "cicd":"ci/cd","ci cd":"ci/cd","continuous integration":"ci/cd","github action":"github actions","large language model":"llm","large language models":"llm","genai":"generative ai","gen ai":"generative ai",
 "dsa":"data structures","data structure":"data structures","algorithm":"algorithms","unit tests":"unit testing","data viz":"data visualization","hugging-face":"hugging face","neural network":"neural networks"}
