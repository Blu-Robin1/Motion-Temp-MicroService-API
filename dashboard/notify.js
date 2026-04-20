/* ADD TO TOP OF JS FILE */
// const NOTIFIER_API_URL = "/notifier/alerts";
// const sendAlert = async (alertMessage) => {
//     const alertData = {
//         alert_id: crypto.randomUUID(), // Generates a unique ID for the mapping
//         message: alertMessage
//     };

//     try {
//         const response = await fetch(NOTIFIER_API_URL, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify(alertData),
//         });

//         if (response.status === 201) {
//             console.log("Alert successfully sent to Notifier service");
//         }
//     } catch (error) {
//         console.error("Failed to send alert:", error);
//     }
// };
// const updateErrorMessages = (message) => {
//     const id = Date.now();
    
//     // 1. Log the error to the Notifier microservice (New Logic)
//     sendAlert(message);

//     // 2. Existing UI logic to show the error box
//     const msg = document.createElement("div");
//     msg.id = `error-${id}`;
//     msg.innerHTML = `<p>Something happened at ${getLocaleDateStr()}!</p><code>${message}</code>`;
    
//     const messagesContainer = document.getElementById("messages");
//     messagesContainer.style.display = "block";
//     messagesContainer.prepend(msg);

//     setTimeout(() => {
//         const elem = document.getElementById(`error-${id}`);
//         if (elem) { elem.remove(); }
//     }, 7000);
// };