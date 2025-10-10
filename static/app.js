document.getElementById('whatsapp-form').addEventListener('submit', function(event) {
  event.preventDefault();

  const form = event.target;
  const submitButton = form.querySelector('button[type="submit"]');
  const originalButtonText = submitButton.innerHTML;
  const feedbackDiv = document.getElementById('form-feedback');

  // Clear previous feedback
  feedbackDiv.innerHTML = '';

  // Get form data
  const formData = {
    nome: document.getElementById('nome').value,
    email: document.getElementById('email').value,
    telefone: document.getElementById('telefone').value,
    empresa: document.getElementById('empresa').value
  };

  // Disable button and show loading state with a spinner
  submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
  submitButton.disabled = true;

  // Send data to the backend
  fetch('http://127.0.0.1:8000/api/contact', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => { throw new Error(err.detail || 'Ocorreu um erro no servidor.'); });
    }
    return response.json();
  })
  .then(data => {
    console.log('Success:', data);
    // Show success message
    feedbackDiv.innerHTML = '<div class="alert alert-success">Mensagem enviada com sucesso! Entraremos em contato em breve.</div>';
    form.reset();
  })
  .catch((error) => {
    console.error('Error:', error);
    // Show error message
    feedbackDiv.innerHTML = `<div class="alert alert-danger">Houve um erro ao enviar sua mensagem. Por favor, tente novamente.</div>`;
  })
  .finally(() => {
    // Restore button state after a delay, allowing user to see the feedback message
    setTimeout(() => {
      submitButton.innerHTML = originalButtonText;
      submitButton.disabled = false;
      // Optionally clear the feedback message after more time
      setTimeout(() => {
        if (feedbackDiv.querySelector('.alert-success')) {
          feedbackDiv.innerHTML = '';
        }
      }, 4000); // Clear success message after 4 more seconds
    }, 2000); // Re-enable button after 2 seconds
  });
});