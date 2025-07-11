// src/App.js
import React, { useState } from "react";
import "./App.css";
import { analyzeDocument, refineContent, generatePlan } from "./api";
import jsPDF from "jspdf";
import { saveAs } from "file-saver";
import PptxGenJS from "pptxgenjs";
import { Document, Packer, Paragraph, TextRun } from "docx";

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [provider, setProvider] = useState("groq");
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [planMode, setPlanMode] = useState("auto");
  const [numDays, setNumDays] = useState("");
  const [hoursPerDay, setHoursPerDay] = useState("");
  const [feedback, setFeedback] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleAnalyze = async () => {
    if (!file) return alert("Please upload a file.");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("provider", provider);
    try {
      const result = await analyzeDocument(formData);
      setAnalysis(result);
    } catch {
      alert("Analysis error");
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    try {
      const result = await generatePlan({
        training_modules: analysis.training_modules,
        plan_mode: planMode,
        num_days: planMode === "manual" ? Number(numDays) : undefined,
        hours_per_day: planMode === "manual" ? Number(hoursPerDay) : undefined,
      });
      setPlan(result.plan);
    } catch {
      alert("Plan generation error");
    }
  };

  const handleRefine = async () => {
    if (!feedback || !analysis) {
      alert("Please enter feedback first.");
      return;
    }
  
    try {
      const refined = await refineContent({
        text: analysis,
        user_feedback: feedback,
      });
      setAnalysis(refined);
      setFeedback("");  // امسح الملاحظات بعد التعديل
    } catch (err) {
      console.error("Refinement error:", err);
      alert("Something went wrong during refinement.");
    }
  };
  

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    doc.text("📄 La5asni Analysis", 10, 10);
    doc.text(`Summary: ${analysis.summary}`, 10, 20);

    let y = 30;
    doc.text("Key Points:", 10, y);
    y += 10;
    analysis.key_points.forEach((point) => {
      doc.text(`- ${point}`, 12, y);
      y += 10;
    });

    y += 10;
    doc.text("Modules:", 10, y);
    y += 10;
    analysis.training_modules.forEach((mod) => {
      doc.text(`${mod.title} — ${mod.estimated_minutes} mins`, 12, y);
      y += 10;
      doc.text(mod.description, 14, y);
      y += 10;
    });

    doc.save("analysis.pdf");
  };

  const handleDownloadWord = () => {
    const doc = new Document({
      sections: [
        {
          children: [
            new Paragraph({ text: "La5asni Analysis", heading: "Title" }),
            new Paragraph("📌 Summary:"),
            new Paragraph(analysis.summary),
            new Paragraph("✅ Key Points:"),
            ...analysis.key_points.map((p) => new Paragraph(`• ${p}`)),
            new Paragraph("📚 Training Modules:"),
            ...analysis.training_modules.map(
              (m) =>
                new Paragraph({
                  children: [
                    new TextRun({ text: `${m.title} — ${m.estimated_minutes} mins`, bold: true }),
                    new TextRun({ text: `\n${m.description}` }),
                  ],
                })
            ),
          ],
        },
      ],
    });

    Packer.toBlob(doc).then((blob) => saveAs(blob, "analysis.docx"));
  };

  const handleDownloadPPT = () => {
    const pptx = new PptxGenJS();
    pptx.addSlide().addText("La5asni Summary", { x: 1, y: 0.5, fontSize: 18 });
    pptx.addSlide().addText(analysis.summary, { x: 1, y: 1, fontSize: 14 });

    const keySlide = pptx.addSlide();
    keySlide.addText("Key Points", { x: 1, y: 0.5, fontSize: 18 });
    keySlide.addText(analysis.key_points.map((p) => `• ${p}`).join("\n"), { x: 1, y: 1, fontSize: 14 });

    const moduleSlide = pptx.addSlide();
    moduleSlide.addText("Training Modules", { x: 1, y: 0.5, fontSize: 18 });
    analysis.training_modules.forEach((mod, i) => {
      moduleSlide.addText(`${i + 1}. ${mod.title}`, { x: 1, y: 1 + i * 1, fontSize: 14 });
    });

    pptx.writeFile("analysis.pptx");
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2>📄 La5asni - Document Analyzer</h2>
        <p>Upload a training document and extract insights in seconds.</p>
        <div className="controls">
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="groq">Groq</option>
            <option value="gemini">Gemini</option>
          </select>
          <input type="file" accept=".pdf,.docx" onChange={handleFileChange} />
          <button onClick={handleAnalyze}>{loading ? "Processing..." : "Analyze"}</button>
        </div>
      </header>

      {analysis && (
        <div className="results">
          <h3>📌 Summary</h3>
          <p>{analysis.summary}</p>

          <h3>✅ Key Points</h3>
          <ul>{analysis.key_points.map((p, i) => <li key={i}>{p}</li>)}</ul>

          <h3>📚 Training Modules</h3>
          <ul>
            {analysis.training_modules.map((m, i) => (
              <li key={i}>
                <strong>{m.title}</strong> — {m.estimated_minutes} mins
                <p>{m.description}</p>
              </li>
            ))}
          </ul>

          <div className="refine-ui">
            <textarea
              placeholder="Suggest improvements..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
            <button onClick={handleRefine}>✨ Refine Output</button>
          </div>

          <div className="plan-controls">
            <label>
              Plan Mode:
              <select value={planMode} onChange={(e) => setPlanMode(e.target.value)}>
                <option value="auto">Auto</option>
                <option value="manual">Manual</option>
              </select>
            </label>
            {planMode === "manual" && (
              <>
                <input
                  type="number"
                  placeholder="Number of days"
                  value={numDays}
                  onChange={(e) => setNumDays(e.target.value)}
                />
                <input
                  type="number"
                  placeholder="Hours per day"
                  value={hoursPerDay}
                  onChange={(e) => setHoursPerDay(e.target.value)}
                />
              </>
            )}
            <button onClick={handleGeneratePlan}>📅 Generate Training Plan</button>
          </div>

          <div className="action-buttons">
            <button onClick={handleDownloadPDF}>⬇️ Export PDF</button>
            <button onClick={handleDownloadWord}>⬇️ Export DOCX</button>
            <button onClick={handleDownloadPPT}>⬇️ Export PPT</button>
          </div>

          {plan && (
            <>
              <h3>🗓 Training Plan</h3>
              {plan.map((d, i) => (
                <div key={i}>
                  <h4>Day {d.day} - {d.total_minutes} mins</h4>
                  <ul>
                    {d.sessions.map((s, j) => (
                      <li key={j}>
                        <strong>{s.title}</strong> — {s.duration} mins
                        <p>{s.description}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
