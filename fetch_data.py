import pyodbc
import pandas as pd

def fetch_data():
    server = '.'
    database = 'SjDataModel'
    username = 'sa'
    password = 'Aa1234'

    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    query = """
    SELECT 
        h.NodeId, 
        h.ParentId, 
        h.Level1, 
        h.Level2, 
        h.Level3, 
        h.Level4, 
        h.FullPath, 
        h.Level, 
        h.Title,
        COUNT(e.NATIONAL_No) AS NationalIdCount,
        SUM(CASE WHEN e.SEX_CODE = '1' THEN 1 ELSE 0 END) AS MaleCount,
        SUM(CASE WHEN e.SEX_CODE = '2' THEN 1 ELSE 0 END) AS FemaleCount,
        e.EMPLOYM_TYPE
    FROM 
        HierarchyTable_Final h
    LEFT JOIN 
        Employees e
    ON 
        h.NodeId = e.HoldingCode
    GROUP BY 
        h.NodeId, h.ParentId, h.Level1, h.Level2, h.Level3, h.Level4, 
        h.FullPath, h.Level, h.Title, e.EMPLOYM_TYPE
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
