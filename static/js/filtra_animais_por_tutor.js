(function () {
    function init() {
        if (!window.django || !window.django.jQuery) {
            setTimeout(init, 100);
            return;
        }

        const $ = window.django.jQuery;
        const tutorSelect = $('#id_tutor');
        const animalSelect = $('#id_animal');

        if (tutorSelect.length === 0 || animalSelect.length === 0) {
            return;
        }

        let ignorarProximoChangeTutor = false;

        function aplicarFiltro() {
            const select2Data = animalSelect.data('select2');
            if (!select2Data) {
                setTimeout(aplicarFiltro, 200);
                return;
            }

            const ajaxOptions = select2Data.options.options.ajax;
            if (!ajaxOptions) {
                return;
            }

            const originalDataFunction = ajaxOptions.data;

            ajaxOptions.data = function (params) {
                let result = {};
                if (typeof originalDataFunction === 'function') {
                    result = originalDataFunction.call(this, params) || {};
                } else {
                    result = { term: params.term, page: params.page };
                }
                result.tutor_id = tutorSelect.val() || '';
                return result;
            };
        }

        function preencherTutorPeloAnimal(animalId) {
            if (!animalId) return;

            $.get('/cadastros/tutor-do-animal/', { animal_id: animalId })
                .done(function (data) {
                    if (data.tutor_id) {
                        const tutorAtual = tutorSelect.val();
                        if (String(tutorAtual) !== String(data.tutor_id)) {
                            ignorarProximoChangeTutor = true;
                            const option = new Option(data.tutor_nome, data.tutor_id, true, true);
                            tutorSelect.append(option).trigger('change');
                        }
                    }
                });
        }

        tutorSelect.on('change', function () {
            if (ignorarProximoChangeTutor) {
                ignorarProximoChangeTutor = false;
                return;
            }

            const tutorId = tutorSelect.val();
            const animalId = animalSelect.val();

            if (!animalId || !tutorId) return;

            $.get('/cadastros/tutor-do-animal/', { animal_id: animalId })
                .done(function (data) {
                    if (String(data.tutor_id) !== String(tutorId)) {
                        animalSelect.val(null).trigger('change');
                    }
                });
        });

        animalSelect.on('change', function () {
            const animalId = animalSelect.val();
            if (animalId && !tutorSelect.val()) {
                preencherTutorPeloAnimal(animalId);
            }
        });

        aplicarFiltro();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();