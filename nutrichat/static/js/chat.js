// ============================================================
// NutriChat — chat.js
// Lógica do frontend: envio de mensagens, sidebar, modal de perfil
// ============================================================

// --- Seletores de elementos principais ---
const messagesArea   = document.getElementById('messagesArea');
const messageInput   = document.getElementById('messageInput');
const sendBtn        = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const charCount      = document.getElementById('charCount');

// Sidebar
const sidebar        = document.getElementById('sidebar');
const hamburger      = document.getElementById('hamburger');
const sidebarClose   = document.getElementById('sidebarClose');
const sidebarOverlay = document.getElementById('sidebarOverlay');

// Modal de perfil
const profileModal   = document.getElementById('profileModal');
const profileForm    = document.getElementById('profileForm');
const modalClose     = document.getElementById('modalClose');
const btnEditProfile = document.getElementById('btnEditProfile');
const btnHeaderProfile = document.getElementById('btnHeaderProfile');
const imcPreview     = document.getElementById('imcPreview');
const imcPreviewVal  = document.getElementById('imcPreviewVal');
const imcPreviewClass = document.getElementById('imcPreviewClass');

// Botões de ação
const btnClearChat   = document.getElementById('btnClearChat');
const quickChips     = document.getElementById('quickChips');

// ============================================================
// ENVIO DE MENSAGENS
// ============================================================

/**
 * Envia a mensagem para a API e exibe a resposta.
 */
async function sendMessage() {
    const texto = messageInput.value.trim();
    if (!texto || sendBtn.disabled) return;

    // Desativa input durante o envio
    sendBtn.disabled = true;
    messageInput.disabled = true;

    // Exibe mensagem do usuário na tela
    appendMessage('user', texto);
    messageInput.value = '';
    updateCharCount();
    autoResizeInput();

    // Mostra indicador de digitação
    showTyping();
    scrollToBottom();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensagem: texto })
        });

        const data = await response.json();
        hideTyping();

        if (data.resposta) {
            appendMessage('bot', data.resposta);
        } else {
            appendMessage('bot', '⚠ Ocorreu um erro. Tente novamente em instantes.');
        }
    } catch (error) {
        hideTyping();
        appendMessage('bot', '⚠ Erro de conexão. Verifique sua internet e tente novamente.');
        console.error('Erro ao enviar mensagem:', error);
    } finally {
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
        scrollToBottom();
    }
}

/**
 * Cria e insere um novo balão de mensagem na tela.
 * @param {string} role - 'user' ou 'bot'
 * @param {string} text - Conteúdo da mensagem
 */
function appendMessage(role, text) {
    // Remove a tela de boas-vindas se existir
    const welcome = document.querySelector('.welcome-screen');
    if (welcome) welcome.remove();

    const isUser = role === 'user';
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    // Formata o texto: quebras de linha → <br>
    const formattedText = escapeHtml(text).replace(/\n/g, '<br>');

    // Hora atual
    const agora = new Date();
    const hora = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    // Avatar do usuário (inicial do nome)
    const userInitial = document.querySelector('.user-avatar.user-avatar')?.textContent || '?';

    div.innerHTML = isUser
        ? `<div class="msg-bubble">
               <div class="msg-text">${formattedText}</div>
               <div class="msg-time">${hora}</div>
           </div>
           <div class="msg-avatar user-avatar">${userInitial}</div>`
        : `<div class="msg-avatar bot-avatar">🥗</div>
           <div class="msg-bubble">
               <div class="msg-text">${formattedText}</div>
               <div class="msg-time">${hora}</div>
           </div>`;

    messagesArea.appendChild(div);
    scrollToBottom();
}

/** Escapa HTML para evitar XSS */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

/** Rola a área de mensagens para o final */
function scrollToBottom() {
    setTimeout(() => {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }, 50);
}

/** Exibe o indicador de digitação */
function showTyping() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

/** Oculta o indicador de digitação */
function hideTyping() {
    typingIndicator.style.display = 'none';
}

// ============================================================
// EVENTOS DE INPUT
// ============================================================

/** Atualiza contador de caracteres */
function updateCharCount() {
    const count = messageInput.value.length;
    charCount.textContent = `${count}/1000`;
    charCount.style.color = count > 900 ? '#fca5a5' : 'var(--text-muted)';
}

/** Redimensiona o textarea automaticamente */
function autoResizeInput() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

// Envio com Enter (Shift+Enter = nova linha)
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput.addEventListener('input', () => {
    updateCharCount();
    autoResizeInput();
});

// Botão de envio
sendBtn.addEventListener('click', sendMessage);

// ============================================================
// CHIPS DE SUGESTÃO RÁPIDA
// ============================================================

/** Envia uma mensagem pré-definida ao clicar em um chip */
function setupChips(container) {
    if (!container) return;
    container.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const msg = chip.dataset.msg;
            if (msg) {
                messageInput.value = msg;
                sendMessage();
            }
        });
    });
}

// Chips da sidebar e boas-vindas
setupChips(quickChips);
setupChips(document.querySelector('.welcome-chips'));

// ============================================================
// SIDEBAR — Toggle mobile
// ============================================================

function openSidebar() {
    sidebar.classList.add('open');
    sidebarOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

hamburger.addEventListener('click', openSidebar);
sidebarClose.addEventListener('click', closeSidebar);
sidebarOverlay.addEventListener('click', closeSidebar);

// ============================================================
// MODAL DE EDIÇÃO DE PERFIL
// ============================================================

function openProfileModal() {
    profileModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeProfileModal() {
    profileModal.classList.remove('active');
    document.body.style.overflow = '';
}

btnEditProfile?.addEventListener('click', () => { closeSidebar(); openProfileModal(); });
btnHeaderProfile?.addEventListener('click', openProfileModal);
modalClose.addEventListener('click', closeProfileModal);

// Fecha modal ao clicar fora
profileModal.addEventListener('click', (e) => {
    if (e.target === profileModal) closeProfileModal();
});

// Preview de IMC em tempo real no modal
const editPeso   = document.getElementById('editPeso');
const editAltura = document.getElementById('editAltura');

function updateImcPreview() {
    const peso   = parseFloat(editPeso?.value);
    const altura = parseFloat(editAltura?.value);

    if (peso > 0 && altura > 0) {
        const imc = (peso / (altura * altura)).toFixed(2);
        let classe = '';
        if (imc < 18.5)       classe = 'Abaixo do peso';
        else if (imc < 25.0)  classe = 'Peso normal ✓';
        else if (imc < 30.0)  classe = 'Sobrepeso';
        else if (imc < 35.0)  classe = 'Obesidade grau I';
        else if (imc < 40.0)  classe = 'Obesidade grau II';
        else                  classe = 'Obesidade grau III';

        imcPreviewVal.textContent  = imc;
        imcPreviewClass.textContent = `— ${classe}`;
        imcPreview.style.display   = 'flex';
    } else {
        imcPreview.style.display = 'none';
    }
}

editPeso?.addEventListener('input', updateImcPreview);
editAltura?.addEventListener('input', updateImcPreview);

// Salva o perfil via API
profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = profileForm.querySelector('.btn-primary');
    btn.disabled = true;
    btn.textContent = 'Salvando...';

    const payload = {
        peso:            parseFloat(document.getElementById('editPeso').value) || null,
        altura:          parseFloat(document.getElementById('editAltura').value) || null,
        idade:           parseInt(document.getElementById('editIdade').value) || null,
        objetivo:        document.getElementById('editObjetivo').value,
        nivel_atividade: document.getElementById('editNivel').value
    };

    try {
        const res = await fetch('/api/atualizar-perfil', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
            closeProfileModal();
            // Recarrega a página para atualizar o IMC e dados do perfil
            window.location.reload();
        } else {
            alert('Erro ao salvar o perfil. Tente novamente.');
        }
    } catch (err) {
        alert('Erro de conexão. Verifique sua internet.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Salvar alterações';
    }
});

// ============================================================
// LIMPAR HISTÓRICO
// ============================================================

btnClearChat?.addEventListener('click', async () => {
    if (!confirm('Tem certeza que deseja apagar todo o histórico de conversas?')) return;

    try {
        await fetch('/api/limpar-chat', { method: 'POST' });
        window.location.reload();
    } catch (err) {
        alert('Erro ao limpar histórico.');
    }
});

// ============================================================
// INICIALIZAÇÃO
// ============================================================

// Rola para o fim ao carregar a página (se há histórico)
scrollToBottom();

// Foca no input ao carregar
messageInput.focus();

// Inicializa contador de caracteres
updateCharCount();
