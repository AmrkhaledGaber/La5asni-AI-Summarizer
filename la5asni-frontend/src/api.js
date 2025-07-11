const BASE_URL = "http://127.0.0.1:8000/api/v1";

export const analyzeDocument = async (formData) => {
  const res = await fetch(`${BASE_URL}/analyze/`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Analysis failed.");
  return await res.json();
};

export const refineContent = async (jsonData) => {
    const res = await fetch(`${BASE_URL}/refine/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(jsonData),
    });
    if (!res.ok) throw new Error("Refinement failed.");
    return await res.json();
  };
  

export const generatePlan = async (planData) => {
  const res = await fetch(`${BASE_URL}/plan/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(planData),
  });
  return await res.json();
};
