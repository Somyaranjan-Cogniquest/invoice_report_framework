from utils.lineitem_report import create_lineitem_report
import pandas as pd

from db.db_helper import (
    get_kv_llama_values,
    get_kv_bbox_details_annotated
)

from utils.comparator import compare_values


dbstring = '35.244.41.206#root#~0g-"&~[>DAY]p|&#eval_2_db2#3306'

#doc_ids = [
#    63313,
#    63314,
#    63315

#]

doc_ids = list(range(63313, 63320))

detailed_rows = []

summary_rows = []

topic_summary = {}
EXPECTED_TOPICS = [
    "InvoiceHeader",
    "SupplierName",
    "SupplierAddress",
    "SupplierTaxNumber",
    "BuyerName",
    "BuyerAddress",
    "BuyerTaxNumber",
    "InvoiceNumber",
    "InvoiceIssueDate",
    "InvoiceDueDate",
    "PurchaseOrderNumber",
    "EWayBillNumber",
    "TotalAmountBeforeTax",
    "TotalTax",
    "TotalAmountAfterTax",
    "GRNSeal",
    "IRNSticker",
    "IRNStickerWHDocumentID",
    "IRNStickerInvoiceQty",
    "AuthorisedSignature",
    "HSNCodePresence"
]


for doc_id in doc_ids:

    print(f"Processing doc_id: {doc_id}")

    llama_data = get_kv_llama_values(dbstring, doc_id)

    review_data = get_kv_bbox_details_annotated(doc_id, dbstring)

    matched = 0
    error = 0
    missed = 0

    #topics = set(llama_data.keys()) | set(review_data.keys())
    topics = EXPECTED_TOPICS

    for topic in topics:

        review_value = review_data.get(topic, "")

        llama_value = llama_data.get(topic, "")

        match = 0
        err = 0
        miss = 0

        if not str(review_value).strip() and not str(llama_value).strip():
          match = 0
          err = 0
          miss = 0     
          
        # Missed
        elif review_value and not llama_value:
           miss = 1
           missed += 1

        # Match
        elif compare_values(review_value, llama_value):
             match = 1
             matched += 1

        # Error
        else:
            err = 1
            error += 1

        # Detailed Report
        detailed_rows.append({

            "doc_id": doc_id,
            "topic": topic,
            "review_value": review_value,
            "llama_value": llama_value,
            "match": match,
            "error": err,
            "missed": miss
        })

        # Topic Summary
        if topic not in topic_summary:

            topic_summary[topic] = {
                "matched": 0,
                "error": 0,
                "missed": 0
            }

        topic_summary[topic]["matched"] += match
        topic_summary[topic]["error"] += err
        topic_summary[topic]["missed"] += miss

    # Document Summary
    #total_dp = matched + error + missed
    total_dp = len(EXPECTED_TOPICS)

    precision = (
        matched / (matched + error)
        if (matched + error)
        else 0
    )

    recall = (
        matched / (matched + missed)
        if (matched + missed)
        else 0
    )

    summary_rows.append({

        "doc_id": doc_id,
        "total_dp": total_dp,
        "matched": matched,
        "error": error,
        "missed": missed,
        "precision": round(precision, 2),
        "recall": round(recall, 2)
    })


# Create DataFrames

detailed_df = pd.DataFrame(detailed_rows)

summary_df = pd.DataFrame(summary_rows)

# Calculate Average Precision & Recall

avg_precision = summary_df["precision"].mean()

avg_recall = summary_df["recall"].mean()

# Add AVG row

avg_row = pd.DataFrame([{

    "doc_id": "AVG",
    "total_dp": "",
    "matched": "",
    "error": "",
    "missed": "",
    "precision": round(avg_precision, 2),
    "recall": round(avg_recall, 2)

}])

# Append AVG row

summary_df = pd.concat(
    [summary_df, avg_row],
    ignore_index=True
)

topic_df = pd.DataFrame([
    {"topic": k, **v}
    for k, v in topic_summary.items()
])


# Export Reports

with pd.ExcelWriter("reports/DataFields_report.xlsx") as writer:

    detailed_df.to_excel(
        writer,
        sheet_name="Detailed_Report",
        index=False
    )

    summary_df.to_excel(
        writer,
        sheet_name="Doc_Summary",
        index=False
    )

    topic_df.to_excel(
        writer,
        sheet_name="Topic_Summary",
        index=False
    )

print("✅ Reports Generated Successfully")

# Generate LineItem Report
create_lineitem_report(dbstring, doc_ids)



#python generate_report.py