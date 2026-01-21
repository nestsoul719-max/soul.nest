// ===============================
// SoulNest – Tagda Frontend Logic
// ===============================

const API_URL = "https://calm-friend.preview.emergentagent.com/api/chat"; 
// (local ho to http://localhost:8001/api/chat)

// DOM
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");

let conversationId = null;

// Utility: add message
function addMessage(text, sender = "ai") {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Typing indicator
function showTyping() {
  const typing = document.createElement("div");
  typing.className = "typing";
  typing.id = "typing";
  typing.innerText = "SoulNest is typing…";
  chatBox.appendChild(typing);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}

// First welcome message
window.addEventListener("load", () => {
  setTimeout(() => {
    addMessage(
      "Hey 🤍 main yahin hoon.\nJo bhi dil me hai, bina dare likh do.",
      "ai"
    );
  }, 600);
});

// Chat submit
if (chatForm) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const userText = chatInput.value.trim();
    if (!userText) return;

    addMessage(userText, "user");
    chatInput.value = "";
    showTyping();

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          conversation_id: conversationId,
          user_id: "default_user"
        })
      });

      const data = await res.json();
      removeTyping();

      if (data.message) {
        addMessage(data.message, "ai");
        conversationId = data.conversation_id;
      } else {
        addMessage("Thoda sa issue aa gaya 😔 phir try karo.", "ai");
      }

    } catch (err) {
      removeTyping();
      addMessage(
        "Server se connect nahi ho pa raha 💔\nThodi der baad try karo.",
        "ai"
      );
      console.error(err);
    }
  });
}
