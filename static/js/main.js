document.addEventListener('DOMContentLoaded', function () {
  var searchForm = document.getElementById('search-form');
  var searchInput = document.getElementById('search-input');
  var loadMoreBtn = document.getElementById('load-more');
  var peopleContainer = document.getElementById('people-container');
  var currentOffsetSpan = document.getElementById('current-offset');
  var recordsPerPage = parseInt(peopleContainer.dataset.recordsPerPage);

  function updateOffsetDisplay() {
    var currentOffset = loadMoreBtn.getAttribute('data-offset');
    currentOffsetSpan.textContent = currentOffset;
  }

  function getCurrentRowCount() {
    return document.querySelectorAll('#people-tbody tr').length;
  }

  searchForm?.addEventListener('htmx:configRequest', function (event) {
    event.detail.parameters['query'] = searchInput.value;
  });

  searchForm?.addEventListener('htmx:afterOnLoad', function (event) {
    loadMoreBtn.setAttribute('data-offset', recordsPerPage);
    updateOffsetDisplay();

    var triggerHeader = event.detail.xhr.getResponseHeader('HX-Trigger');
    if (triggerHeader && JSON.parse(triggerHeader).noMoreRecords) {
      loadMoreBtn.style.display = 'none';
    } else {
      loadMoreBtn.style.display = 'block';
    }

    peopleContainer.setAttribute('data-total-records', getCurrentRowCount().toString());
    updateOffsetDisplay();
  });

  loadMoreBtn?.addEventListener('htmx:configRequest', function (event) {
    event.detail.parameters['offset'] = this.getAttribute('data-offset');
    event.detail.parameters['query'] = searchInput.value;
  });

  loadMoreBtn?.addEventListener('htmx:afterOnLoad', function (event) {
    var currentRowCount = getCurrentRowCount();
    this.setAttribute('data-offset', currentRowCount.toString());

    peopleContainer.setAttribute('data-total-records', currentRowCount.toString());

    var triggerHeader = event.detail.xhr.getResponseHeader('HX-Trigger');
    if (triggerHeader && JSON.parse(triggerHeader).noMoreRecords) {
      this.style.display = 'none';
    }
    updateOffsetDisplay();
  });
});

function closeModal() {
  const modal = document.getElementById('modal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

// Handle form submissions
document.addEventListener('htmx:afterOnLoad', function (event) {
  const form = event.target.closest('form');
  if (form?.id === 'person-form') {
    const formResult = document.getElementById('form-result');
    if (formResult) {
      formResult.innerHTML = '<p class="text-green-500">Person updated successfully!</p>';
      setTimeout(closeModal, 1000);
    }
  }
});
