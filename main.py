# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

def get_db_connection():
    return psycopg2.connect(
        dsn=os.getenv("POSTGRES_URL"),
        sslmode="require"
    )

@app.route("/api/underwriting-summary", methods=["GET"])
def underwriting_summary():
    limit = int(request.args.get("limit", 50))     # default 50
    offset = int(request.args.get("offset", 0))    # default 0
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT policy_id, classification, tiv, total_premium,
               primary_risk_state, line_of_business, construction_type,
               oldest_building, reasoning
        FROM underwriting_results
        ORDER BY policy_id
        LIMIT %s OFFSET %s;
    """, (limit, offset))
    rows = cur.fetchall()
    
    # get total count for pagination info
    cur.execute("SELECT COUNT(*) FROM underwriting_results;")
    total_count = cur.fetchone()["count"]
    
    cur.close()
    conn.close()
    
    return jsonify({
        "data": rows,
        "total": total_count,
        "limit": limit,
        "offset": offset
    })

# NEW ENDPOINT: Get individual policy by ID
@app.route("/api/underwriting-summary/<policy_id>", methods=["GET"])
def get_policy(policy_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT policy_id, classification, tiv, total_premium,
               primary_risk_state, line_of_business, construction_type,
               oldest_building, reasoning
        FROM underwriting_results
        WHERE policy_id = %s;
    """, (policy_id,))
    policy = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if policy:
        return jsonify(policy)
    else:
        return jsonify({"error": "Policy not found"}), 404

if __name__ == "__main__":
    app.run(port=8000, debug=True)