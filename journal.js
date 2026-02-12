/* ============================================================
   JOURNAL.JS - النسخة النهائية المعتمدة لمشروع "أناه"
   الربط الكامل مع Firebase وسيرفر Render (AI)
============================================================ */

function wordCount(t = "") {
  if (!t) return 0;
  const m = t.trim().match(/\S+/g);
  return m ? m.length : 0;
}

/* 1) DOM Elements */
const note = document.getElementById("note");
const saveBtn = document.getElementById("save");
const clearBtn = document.getElementById("clearToday");
const entriesEl = document.getElementById("entries");
const allEntries = document.getElementById("allEntries");
const showAllBtn = document.getElementById("showAll");
const ratingText = document.getElementById("ratingText");
const curEl = document.getElementById("curStreak");
const bestEl = document.getElementById("bestStreak");
const achvCard = document.getElementById("achievements");
const showAchvBtn = document.getElementById("showAchv");
const noteInfo = document.getElementById("noteInfo");
const viewModal = document.getElementById("viewModal");
const closeModal = document.getElementById("closeModal");
const viewContent = document.getElementById("viewContent");
const deleteModal = document.getElementById("deleteConfirmModal");
const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
const emptyNoteModal = document.getElementById("emptyNoteModal");
const closeEmptyNoteBtn = document.getElementById("closeEmptyNoteModal");

if (closeEmptyNoteBtn) {
  closeEmptyNoteBtn.onclick = () => {
    if (emptyNoteModal) emptyNoteModal.hidden = true;
  };
}

let selectedRating = 0;

/* 2) Rating System */
function initRating() {
  const ratingEl = document.getElementById("rating");
  if (!ratingEl) return;
  const stars = Array.from(ratingEl.querySelectorAll("button[data-v]"));
  
  function paint(n) {
    selectedRating = n;
    stars.forEach((btn) => {
      const v = Number(btn.dataset.v || "0");
      btn.classList.toggle("active", v <= n);
    });
    if (ratingText) ratingText.textContent = `قيّم يومك: ${n}/5`;
  }

  ratingEl.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-v]");
    if (btn) paint(Number(btn.dataset.v || "0"));
  });
  paint(0);
}

if (closeModal) closeModal.onclick = () => (viewModal.hidden = true);

/* ------------------------------------------------------------
   3) SAVE Journal Entry (الارتباط بـ Render و Firebase)
------------------------------------------------------------ */
if (saveBtn && note) {
  saveBtn.onclick = async () => {
    const text = note.value.trim();
    if (!text) { 
      if (emptyNoteModal) emptyNoteModal.hidden = false; 
      return; 
    }

    const user = firebase.auth().currentUser;
    if (!user) { 
      alert("يرجى تسجيل الدخول أولاً"); 
      return; 
    }

    try {
      saveBtn.disabled = true;
      saveBtn.textContent = "جاري تحليل مشاعرك...";

      // 1. الاتصال بالذكاء الاصطناعي (سيرفر Render الداخلي)
      const response = await fetch("/predict", { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text }) 
      });

      if (!response.ok) throw new Error("AI Service Error");

      const data = await response.json();
      const moodResult = data.mood; // استلام النتيجة من Flask

      // 2. حفظ البيانات في Firebase
      const today = new Date().toISOString().split('T')[0];
      await firebase.firestore().collection("users").doc(user.uid)
        .collection("entries").doc(today).set({
          text: text,
          rating: selectedRating,
          words: wordCount(text),
          finalMood: moodResult, 
          savedAt: firebase.firestore.FieldValue.serverTimestamp()
        });

      alert(`تم الحفظ بنجاح! تحليل أناه لمشاعرك: ${moodResult} ✨`);
      
      // إعادة ضبط الواجهة
      note.value = "";
      selectedRating = 0;
      const stars = Array.from(document.querySelectorAll("#rating button[data-v]"));
      stars.forEach(s => s.classList.remove("active"));
      if (ratingText) ratingText.textContent = "قيّم يومك: 0/5";

    } catch (error) {
      console.error("Error details:", error);
      alert("حدث خطأ في الاتصال بالسيرفر. تأكدي أن موقع Render يعمل (Live).");
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = "حفظ المذكرة";
    }
  };
}

/* ------------------------------------------------------------
   4) Delete Today's Entry
------------------------------------------------------------ */
if (clearBtn) clearBtn.onclick = () => (deleteModal.hidden = false);

if (confirmDeleteBtn) {
  confirmDeleteBtn.onclick = async () => {
    const user = firebase.auth().currentUser;
    if (!user) return;

    try {
      const today = new Date().toISOString().split('T')[0];
      await firebase.firestore().collection("users").doc(user.uid)
        .collection("entries").doc(today).delete();
      
      note.value = "";
      deleteModal.hidden = true;
      alert("تم حذف مذكرة اليوم.");
    } catch (error) {
      console.error("Error deleting entry:", error);
      alert("حدث خطأ أثناء الحذف.");
    }
  };
}

if (cancelDeleteBtn) cancelDeleteBtn.onclick = () => (deleteModal.hidden = true);

/* ------------------------------------------------------------
   5) UI Toggles & Initialization
------------------------------------------------------------ */
if (showAllBtn) showAllBtn.onclick = () => (allEntries.hidden = !allEntries.hidden);
if (showAchvBtn) showAchvBtn.onclick = () => (achvCard.hidden = !achvCard.hidden);

// تشغيل نظام التقييم
initRating();