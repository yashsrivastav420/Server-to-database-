
const contactForm = document.getElementById("contact-form");
const formStatus = document.getElementById("form-status");

contactForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(contactForm);
    const data = Object.fromEntries(formData.entries());

    formStatus.textContent = "Submitting your enquiry...";

    try {
        const response = await fetch("/api/contact", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Submission failed.");
        }

        formStatus.textContent = result.message;
        contactForm.reset();

    } catch (error) {
        console.error("Contact form error:", error);
        formStatus.textContent =
            error.message || "Could not submit your enquiry. Please try again.";
    }
});
