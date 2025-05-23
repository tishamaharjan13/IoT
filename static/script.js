function showAlert(message, isSuccess = true) {
  const color = isSuccess ? "#28a745" : "#dc3545";
  alert(message);
}

function handleSignup(event) {
  event.preventDefault();

  const email = document.querySelector("#signup-email").value;
  const password = document.querySelector("#signup-password").value;

  if (email && password) {
    showAlert("Sign up successful!");
  } else {
    showAlert("Please fill in all fields!", false);
  }
}

function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  if (email === "tishamaharjan13@gmail.com" && password === "tisha1234") {
    window.location.href = "users.html";
  } else {
    alert("Invalid email or password!");
  }
}

document.getElementById("add-btn").addEventListener("click", function () {
  document.getElementById("add-user").style.display = "block";
  document.getElementById("add-btn").style.display = "none";
  document.getElementById("remove-btn").style.display = "none";
});

// Submit user
document.getElementById("submit-user").addEventListener("click", function () {
  const yourName = document.getElementById("your-name").value;
  if (yourName) {
    alert("User added: " + userName);
    document.getElementById("your-name").value = "";
    document.getElementById("add-user").style.display = "none";
    document.getElementById("add-btn").style.display = "block";
    document.getElementById("remove-btn").style.display = "block";
  } else {
    alert("Please enter a name.");
  }
});

const users = [];

const addBtn = document.getElementById("add-btn");
const removeBtn = document.getElementById("remove-btn");
const addSection = document.getElementById("add-user");
const userList = document.getElementById("user-list");
const userContainer = document.getElementById("user-container");
const submitUser = document.getElementById("submit-user");
const usernameInput = document.getElementById("your-name");

addBtn.onclick = () => {
  addSection.style.display = "block";
  addBtn.style.display = "none";
  removeBtn.style.display = "none";
  userList.style.display = "none";
  document.getElementById("back-btn-container").style.display = "block";
};

// submitUser.onclick = () => {
//   const name = usernameInput.value.trim();
//   if (!name) return alert("Please enter a name.");
//   users.push(name);
//   alert("User added: " + name);
//   usernameInput.value = "";
//   resetView();
// };

removeBtn.onclick = () => {
  addBtn.style.display = "none";
  removeBtn.style.display = "none";
  addSection.style.display = "none";
  userList.style.display = "block";
  // showUsers();
  document.getElementById("back-btn-container").style.display = "block";

  document.getElementById("title").textContent = "Removing User...";
};

function showUsers() {
  userContainer.innerHTML = users.length
    ? users
      .map(
        (user, i) => `
        <li>
          ${user}
          <button class="button" style="width:auto" onclick="removeUser(${i})">Remove</button>
        </li> 
      `
      )
      .join("")
    : "<li>No users added yet.</li>";
}

function removeUser(index) {
  users.splice(index, 1);
  // showUsers();
}

function resetView() {
  addSection.style.display = "none";
  userList.style.display = "none";
  addBtn.style.display = "block";
  removeBtn.style.display = "block";
  document.getElementById("back-btn-container").style.display = "none";
}

const backBtn = document.getElementById("back-btn");

backBtn.onclick = () => {
  userList.style.display = "none";
  addSection.style.display = "none";
  addBtn.style.display = "block";
  removeBtn.style.display = "block";
  document.getElementById("back-btn-container").style.display = "none";
  window.location.reload();
  // document.getElementById("title").textContent = ;
};
