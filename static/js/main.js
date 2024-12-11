document.addEventListener('DOMContentLoaded', function () {
  var searchForm = document.getElementById('search-form');
  var searchInput = document.getElementById('search-input');
  var loadMoreBtn = document.getElementById('load-more');
  var peopleContainer = document.getElementById('people-container');
  var currentOffsetSpan = document.getElementById('current-offset');
  var recordsPerPage = peopleContainer ? parseInt(peopleContainer.dataset.recordsPerPage) : 10;

  function updateOffsetDisplay() {
    if (loadMoreBtn && currentOffsetSpan) {
      var currentOffset = loadMoreBtn.getAttribute('data-offset');
      currentOffsetSpan.textContent = currentOffset;
    }
  }

  function getCurrentRowCount() {
    return document.querySelectorAll('#people-tbody tr').length;
  }

  searchForm?.addEventListener('htmx:configRequest', function (event) {
    event.detail.parameters['query'] = searchInput.value;
  });

  searchForm?.addEventListener('htmx:afterOnLoad', function (event) {
    if (loadMoreBtn) {
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
    }
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

// Store the currently selected row identifiers and descriptions
let selectedManifestIdentifier = null;
let selectedManifestBol = null;
let selectedLineItemIdentifier = null;
let selectedLineItemDescription = null;

// Handle manifest row selection
function selectRow(row, identifier, bol) {
  // Store the selected manifest identifier and BoL
  selectedManifestIdentifier = identifier;
  selectedManifestBol = bol;

  // Remove selected class from all manifest rows
  document.querySelectorAll('#manifest-table tr.selected-row').forEach(tr => {
    tr.classList.remove('selected-row', 'bg-blue-50');
  });

  // Add selected class to clicked manifest row
  row.classList.add('selected-row', 'bg-blue-50');

  // Update the manifest selection display if it exists
  const manifestDisplay = document.querySelector('#selected-manifest-display');
  if (manifestDisplay) {
    manifestDisplay.textContent = selectedManifestBol || '';
  }

  // Clear line item selection when a new manifest is selected
  selectedLineItemIdentifier = null;
  selectedLineItemDescription = null;
  document.querySelectorAll('#lineitem-container tr.selected-row').forEach(tr => {
    tr.classList.remove('selected-row', 'bg-blue-50');
  });
  updateLineItemSelection();
}

// Handle line item row selection
function selectLineItemRow(row, identifier) {
  // Store the selected line item identifier
  selectedLineItemIdentifier = identifier;

  // Store the line item description from the first cell
  const cells = row.querySelectorAll('td div');
  let description = '';
  cells.forEach((cell, index) => {
    if (index < cells.length - 1) { // Skip the last cell (actions cell)
      const text = cell.textContent.trim();
      if (text && text !== 'N/A') {
        description += (description ? ' - ' : '') + text;
      }
    }
  });
  selectedLineItemDescription = description;

  // Remove selected class from all line item rows
  document.querySelectorAll('#lineitem-container tr.selected-row').forEach(tr => {
    tr.classList.remove('selected-row', 'bg-blue-50');
  });

  // Add selected class to clicked line item row
  row.classList.add('selected-row', 'bg-blue-50');

  // Update the selection display
  updateLineItemSelection();
}

// Update the line item selection display
function updateLineItemSelection() {
  const selectionDisplay = document.querySelector('#selected-lineitem-display');
  if (selectionDisplay) {
    selectionDisplay.textContent = selectedLineItemDescription || '';
  }
}

// Add HTMX after-swap event listener to maintain row selections
document.addEventListener('htmx:afterSwap', function (evt) {
  // If this is a line item container swap, scroll it into view
  if (evt.target.id === 'lineitem-container' && evt.target.innerHTML.trim() !== '') {
    evt.target.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Clear line item selection when new line items are loaded
    selectedLineItemIdentifier = null;
    selectedLineItemDescription = null;
    updateLineItemSelection();
  }

  // Restore manifest row selection if we have a selected identifier
  if (selectedManifestIdentifier) {
    const manifestRow = document.querySelector(`#manifest-table tr[data-identifier="${selectedManifestIdentifier}"]`);
    if (manifestRow) {
      manifestRow.classList.add('selected-row', 'bg-blue-50');
      // Restore manifest display
      const manifestDisplay = document.querySelector('#selected-manifest-display');
      if (manifestDisplay) {
        manifestDisplay.textContent = selectedManifestBol || '';
      }
    }
  }

  // Restore line item row selection if we have a selected identifier
  if (selectedLineItemIdentifier) {
    const lineItemRow = document.querySelector(`#lineitem-container tr[data-identifier="${selectedLineItemIdentifier}"]`);
    if (lineItemRow) {
      lineItemRow.classList.add('selected-row', 'bg-blue-50');
      updateLineItemSelection();
    }
  }
});
