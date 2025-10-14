document.addEventListener('DOMContentLoaded', () => {

    async function buscarUsuarios(query) {
        const res = await fetch(`/api/buscar_usuario?q=${encodeURIComponent(query)}`);
        if (res.ok) return await res.json();
        return [];
    }

    function crearInputIntegrante() {
        const div = document.createElement('div');
        div.style.position = 'relative';

        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'Integrantes[]';
        input.placeholder = 'Nombre del integrante';
        input.classList.add('integrante-input');
        input.autocomplete = 'off';

        const ul = document.createElement('ul');
        ul.classList.add('sugerencias');

        div.appendChild(input);
        div.appendChild(ul);

        agregarAutocompletado(input, ul);
        return div;
    }

    function agregarAutocompletado(input, ul) {
        let timeout = null;

        input.addEventListener('input', () => {
            const query = input.value.trim();
            clearTimeout(timeout);
            if (query.length < 2) {
                ul.innerHTML = '';
                return;
            }

            timeout = setTimeout(async () => {
                const resultados = await buscarUsuarios(query);
                ul.innerHTML = '';
                resultados.forEach(u => {
                    const li = document.createElement('li');
                    li.textContent = `${u.nombre} (${u.username})`;
                    li.addEventListener('click', () => {
                        input.value = u.username;
                        ul.innerHTML = '';
                    });
                    ul.appendChild(li);
                });
            }, 300);
        });

        input.addEventListener('blur', () => {
            setTimeout(() => ul.innerHTML = '', 150);
        });
    }

    document.getElementById('add-integrante').addEventListener('click', () => {
        const div = crearInputIntegrante();
        document.getElementById('integrantes-list').appendChild(div);
    });

    document.getElementById('remove-integrante').addEventListener('click', () => {
        const list = document.getElementById('integrantes-list');
        if (list.children.length > 1) {
            list.removeChild(list.lastElementChild);
        }
    });

    // Activar autocompletado en el primer input
    const primerInput = document.querySelector('.integrante-input');
    const primerUl = document.querySelector('.sugerencias');
    agregarAutocompletado(primerInput, primerUl);
});
