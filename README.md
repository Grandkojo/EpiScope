# **EpiScope**  
**AI-Powered Disease Monitoring & Prediction Platform**  

EpiScope is an AI-driven web application designed to **monitor, predict, and provide insights** into disease outbreaks using real-world hospital data. It leverages **machine learning (XGBoost)**, **AI-generated insights (Gemini)**, and interactive dashboards for healthcare decision-making.  

> 🚧 **Note:** The platform is currently in the final stages of development and will be deployed soon at **[episcope.my](https://episcope.my)**. This README will be updated with the live demo link.  

---

## **📹 Demo**  

> 🎥 **Screencast (No Sound)** – The current demo is a silent walkthrough of EpiScope’s interface and functionality.  
A **full narrated demo** will be uploaded soon after deployment.  
[![EpiScope Demo](https://img.youtube.com/vi/KRDk5LWtfSo/0.jpg)](https://youtu.be/KRDk5LWtfSo)

---

## **🎯 Project Overview**  
EpiScope enables hospitals and public health agencies to:  
- **Predict** disease risk probabilities based on patient data.  
- **Explore** historical and aggregated health data through dynamic visualizations.  
- **Understand** AI predictions with SHAP explainability graphs.  
- **Generate** AI-powered summaries and insights using Gemini.  
- **Validate & Improve** the model by confirming, discarding, or correcting predictions — enabling continuous learning.  

---

## **✨ Key Features**  

### **1. Disease Prediction (XGBoost)**  
- Uses **XGBoost** for high-accuracy prediction of disease cases (initial scope: **Diabetes & Malaria**).  
- Predictions are made from **structured hospital health records** and symptom data scored by Gemini.  
- Users can **confirm, correct, or reject** predictions, and the feedback is stored for future model retraining.  

### **2. AI-Generated Insights (Gemini)**  
- Structured prompts generate **summaries, insights, and trends** from filtered datasets.  
- Helps clinicians and decision-makers understand **patterns without manually analyzing raw data**.  

### **3. Interactive Data Visualization**  
- Built with **Plotly/Dash** for rich, dynamic exploration of past and present data.  
- Supports:  
  - Historical trends by disease and location.  
  - National and hospital-specific case counts.  
  - Aggregated Ghana-wide hotspot mapping.  

### **4. Model Explainability (SHAP)**  
- SHAP visualizations show **which features influence each prediction the most**.  
- Empowers healthcare professionals to understand **why** the model made a certain decision.  

---

## **🛠️ Tech Stack**  

| **Component**        | **Technology** |
|----------------------|----------------|
| Backend Framework    | Django (Python) |
| Database             | PostgreSQL |
| AI Models            | XGBoost |
| AI Insights          | Google Gemini API |
| Visualization        | SHAP|
| Containerization     | Docker |
| Cloud AI Platform    | Google Vertex AI |
| Deployment Target    | GCP (Backend) + Vercel (Frontend) |

---

## **📊 Example Workflow**  

1. **Data Input** – User enters patient demographics, locality, pregnancy status, and symptom text.  
2. **Prediction** – XGBoost predicts probability for target disease(s).  
3. **AI Insights** – Gemini analyzes filtered dataset and provides structured insights.  
4. **Explainability** – SHAP graphs show the most influential features for the prediction.  
5. **User Feedback** – Clinician confirms, corrects, or rejects prediction.  
6. **Model Retraining** – Feedback data is stored for future retraining to improve accuracy.  

---

## **🚀 Roadmap**  

- [x] Implement XGBoost prediction for diabetes & malaria  
- [x] SHAP model explainability integration  
- [x] Gemini-powered structured summaries  
- [x] Feedback mechanism for prediction correction  
- [ ] Deploy platform to **episcope.my**  
- [ ] Add LSTM-based forecasting for outbreak trends  
- [ ] Multi-hospital integration and real-time streaming  
