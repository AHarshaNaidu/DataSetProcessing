import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="MIMIC-IV FHIR Dataset Processing")
st.title("MIMIC-IV FHIR Dataset Processing")

# File upload section
st.header("Upload Files")
patient_file = st.file_uploader("Upload Patient.ndjson", type="ndjson")
condition_file = st.file_uploader("Upload Condition.ndjson", type="ndjson")
encounter_file = st.file_uploader("Upload Encounter.ndjson", type="ndjson")
encounter_icu_file = st.file_uploader("Upload EncounterICU.ndjson", type="ndjson")

# Process data
if patient_file and condition_file and (encounter_file or encounter_icu_file):
    # Read files
    patients = [json.loads(line) for line in patient_file.getvalue().decode("utf-8").split("\n") if line]
    conditions = [json.loads(line) for line in condition_file.getvalue().decode("utf-8").split("\n") if line]
    encounters = []
    if encounter_file:
        encounters += [json.loads(line) for line in encounter_file.getvalue().decode("utf-8").split("\n") if line]
    if encounter_icu_file:
        encounters += [json.loads(line) for line in encounter_icu_file.getvalue().decode("utf-8").split("\n") if line]

    # Create patient-condition mapping
    patient_conditions = {}
    for condition in conditions:
        patient_id = condition["subject"]["reference"].split("/")[-1]
        encounter_id = condition["encounter"]["reference"].split("/")[-1]
        encounter = next((e for e in encounters if e["id"] == encounter_id), None)
        if encounter:
            condition_time = datetime.fromisoformat(encounter["period"]["start"]).timestamp()
            condition_code = condition["code"]["coding"][0]["code"]
            condition_desc = condition["code"]["coding"][0]["display"]
            if patient_id in patient_conditions:
                patient_conditions[patient_id].append({"time": condition_time, "code": condition_code, "description": condition_desc})
            else:
                patient_conditions[patient_id] = [{"time": condition_time, "code": condition_code, "description": condition_desc}]

    # Create CSV
    csv_data = []
    for patient_id, conditions in patient_conditions.items():
        for condition in conditions:
            csv_data.append({"pid": patient_id, "time": condition["time"], "code": condition["code"], "description": condition["description"]})
    df = pd.DataFrame(csv_data)

    # Display CSV
    st.header("Processed CSV")
    st.write(df)

    # Download CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="mimic_iv_conditions.csv",
        mime="text/csv",
    )

else:
    st.warning("Please upload all required files.")

# Ask for next steps
st.text_area("What would you like to do next?", height=200)
