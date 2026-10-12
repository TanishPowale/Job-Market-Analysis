\**Job Market Analysis**



The Job Market Analysis system processes job postings using Hadoop HDFS and Apache Spark, stores processed data in SQLite, and provides an interactive Streamlit dashboard to explore job market trends.



\ **Features**



\- Analyze job roles, companies, and locations.

\- Compare remote and onsite job opportunities.

\- Explore hiring trends based on job posting dates.

\- Filter job listings using interactive dashboard controls.

\- View filtered job records and export results to CSV.

\- Process and store cleaned job data using PySpark, HDFS, and Parquet.



\**Technologies Used**



\- Python

\- Apache Hadoop HDFS

\- Apache Spark and PySpark

\- SQLite

\- Streamlit

\- Pandas

\- Parquet



\**Dataset**



The project uses the \[Lynceus Jobs dataset](https://huggingface.co/datasets/Lynceus/jobs), which contains job-posting information such as job title, company, location, remote status, and posting date.



\**Project Structure**



```text

Job-Market-Analysis/

├── dashboard/

│   └── app.py

├── spark/

│   ├── analytics.py

│   ├── parquet\_to\_sqlite.py

│   ├── process\_jobs.py

│   └── update\_dataset.py

├── data/

├── .gitignore

├── requirements.txt

└── README.md

```



\**Prerequisites**



\- Windows

\- Python

\- Java JDK 19

\- Hadoop 3.3.6

\- Apache Spark configured for PySpark

\- Python dependencies listed in `requirements.txt`



\**Installation**



Clone the repository:



```powershell

git clone https://github.com/TanishPowale/Job-Market-Analysis.git

cd Job-Market-Analysis

```



Create and activate the virtual environment:



```powershell

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

```



Install the dependencies:



```powershell

pip install -r requirements.txt

```



\**Starting Hadoop HDFS**



Run these commands in PowerShell from the project directory:



```powershell

$env:JAVA\_HOME = "C:\\PROGRA\~1\\Java\\jdk-19"

$env:HADOOP\_HOME = "C:\\hadoop-3.3.6"

$env:Path = "$env:JAVA\_HOME\\bin;$env:HADOOP\_HOME\\bin;$env:Path"



\& "C:\\hadoop-3.3.6\\sbin\\start-dfs.cmd"

```



Check the running Java processes:



```powershell

jps

```



Open the Hadoop NameNode web interface:



http://localhost:9870



\**Inspecting HDFS**



List the root directory:



```powershell

hdfs dfs -ls /

```



List the Job Market Analysis HDFS directory and its contents:



```powershell

hdfs dfs -ls -R /jobmarket

```



\**Running the Dashboard**



After starting Hadoop and completing the required data-processing steps, run:



```powershell

streamlit run .\\dashboard\\app.py

```



The dashboard is generally available at:



http://localhost:8501



\**Stopping Hadoop HDFS**



When finished, run:



```powershell

\& "C:\\hadoop-3.3.6\\sbin\\stop-dfs.cmd"

```



\**Data Processing Workflow**



1\. Obtain the job-posting dataset.

2\. Store the raw data in Hadoop HDFS.

3\. Clean and transform the data using PySpark.

4\. Store processed data in Parquet format.

5\. Transfer processed data to SQLite.

6\. Explore job market information through the Streamlit dashboard.



\**Future Scope**



\- Add salary and skill-demand analysis when suitable data is available.

\- Explore machine learning for job market trend prediction.

\- Extend dashboard visualizations and reporting features.



\**Author**



\*\*Tanish Powale\*\*



GitHub: \[TanishPowale](https://github.com/TanishPowale)

