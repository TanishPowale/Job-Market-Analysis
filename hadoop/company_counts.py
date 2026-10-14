import os
import subprocess
import uuid
from pathlib import Path

import pandas as pd


def run_hadoop_company_counts(companies):
    companies = companies.fillna("").astype(str).str.strip()
    companies = companies[companies != ""]

    if companies.empty:
        return pd.DataFrame(columns=["Company", "Jobs"])

    run_id = uuid.uuid4().hex[:10]
    project_dir = Path(__file__).resolve().parent.parent
    local_csv = project_dir / "data" / f"filtered_companies_{run_id}.csv"
    hdfs_input = f"/jobmarket/filtered_input_{run_id}"
    hdfs_output = f"/jobmarket/filtered_counts_{run_id}"

    hadoop_home = os.environ.get("HADOOP_HOME", r"C:\hadoop-3.3.6")
    hdfs_cmd = str(Path(hadoop_home) / "bin" / "hdfs.cmd")
    hadoop_cmd = str(Path(hadoop_home) / "bin" / "hadoop.cmd")
    streaming_jar = str(
        Path(hadoop_home) / "share" / "hadoop" / "tools" /
        "lib" / "hadoop-streaming-3.3.6.jar"
    )
    mapper = str(project_dir / "hadoop" / "company_mapper.py")
    reducer = str(project_dir / "hadoop" / "reducer.py")

    input_df = pd.DataFrame({
        "title": [""] * len(companies),
        "company": companies.values,
    })
    local_csv.parent.mkdir(parents=True, exist_ok=True)
    input_df.to_csv(local_csv, index=False, encoding="utf-8")

    try:
        subprocess.run(
            [hdfs_cmd, "dfs", "-put", str(local_csv), hdfs_input],
            check=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        subprocess.run(
            [
                hadoop_cmd, "jar", streaming_jar,
                "-mapper", f"python {mapper}",
                "-reducer", f"python {reducer}",
                "-numReduceTasks", "1",
                "-input", hdfs_input,
                "-output", hdfs_output,
            ],
            check=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        result = subprocess.run(
            [hdfs_cmd, "dfs", "-cat", f"{hdfs_output}/part-*"],
            check=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )

        rows = []
        for line in result.stdout.splitlines():
            if "\t" not in line:
                continue
            name, count = line.rsplit("\t", 1)
            try:
                rows.append((name, int(count)))
            except ValueError:
                continue
        return pd.DataFrame(rows, columns=["Company", "Jobs"])

    except subprocess.CalledProcessError as exc:
        output = []
        if exc.stderr:
            output.append(f"stderr:\n{exc.stderr.strip()}")
        if exc.stdout:
            output.append(f"stdout:\n{exc.stdout.strip()}")
        command = subprocess.list2cmdline(exc.cmd)
        details = "\n".join(output) or "The command returned no output."
        raise RuntimeError(
            f"Hadoop command failed with exit code {exc.returncode}:\n"
            f"{command}\n{details}"
        ) from exc

    finally:
        local_csv.unlink(missing_ok=True)
        subprocess.run(
            [
                hdfs_cmd, "dfs", "-rm", "-r", "-f",
                hdfs_input, hdfs_output,
            ],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
