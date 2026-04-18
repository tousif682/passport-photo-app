const form = document.getElementById("form");
const loader = document.getElementById("loader");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = form.querySelector("input[type='file']");
  
  if (!fileInput.files.length) {
    alert("Please select an image!");
    return;
  }

  loader.style.display = "block";

  const formData = new FormData(form);

  try {
    const res = await fetch("/process", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      throw new Error("Server error!");
    }

    const blob = await res.blob();

    // download file
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "passport.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();

  } catch (err) {
    alert("Something went wrong!");
    console.error(err);
  }

  loader.style.display = "none";
});
