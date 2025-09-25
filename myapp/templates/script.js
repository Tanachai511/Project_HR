document.addEventListener("DOMContentLoaded", function () {
  const authArea = document.getElementById("auth-area");
  if (!authArea) return; // ป้องกัน error ถ้าไม่มี auth-area ในบางหน้า

  const isLoggedIn = localStorage.getItem("loggedIn");

  if (isLoggedIn === "true") {
    authArea.innerHTML = `
      <div class="user-menu">
        <img src="../static/user.png" alt="User" class="user-icon">
        <div class="dropdown">
          <a href="profile.html">โปรไฟล์</a>
          <a href="#" id="logout-btn">ออกจากระบบ</a>
        </div>
      </div>
    `;
  }

  // handle logout
  document.addEventListener("click", function(e) {
    if (e.target.id === "logout-btn") {
      e.preventDefault();
      localStorage.removeItem("loggedIn");
      window.location.href = "index.html";
    }
  });
});
