const repoUrl = 'https://github.com/mthang1201/tweet-covid-sentiment'
const datasetUrl = 'https://crisisnlp.qcri.org/tbcov'

const results = {
  daily: {
    globalCorrelation: '-0.0247',
    temporalImage: './assets/temporal_correlation_daily.png',
    spatialImage: './assets/spatial_correlation_map_daily.png',
    temporalAlt: 'Daily temporal correlation chart',
    spatialAlt: 'Daily spatial correlation map for the continental United States',
  },
  weekly: {
    globalCorrelation: '-0.0442',
    temporalImage: './assets/temporal_correlation_weekly.png',
    spatialImage: './assets/spatial_correlation_map_weekly.png',
    temporalAlt: 'Weekly temporal correlation chart',
    spatialAlt: 'Weekly spatial correlation map for the continental United States',
  },
}

const buttons = Array.from(document.querySelectorAll('.btn-toggle'))
const globalCorrelation = document.querySelector('#globalCorrelation')
const temporalImage = document.querySelector('#temporalImage')
const spatialImage = document.querySelector('#spatialImage')
const runPipelineBtn = document.querySelector('#runPipelineBtn')
const modal = document.querySelector('#pipelineModal')
const closeModalBtn = document.querySelector('#closeModalBtn')

function setLevel(level) {
  const result = results[level]
  if (!result) return

  buttons.forEach((button) => {
    const isActive = button.dataset.level === level
    button.classList.toggle('active', isActive)
    button.setAttribute('aria-selected', String(isActive))
  })

  globalCorrelation.value = result.globalCorrelation
  globalCorrelation.textContent = result.globalCorrelation

  temporalImage.src = result.temporalImage
  temporalImage.alt = result.temporalAlt

  spatialImage.src = result.spatialImage
  spatialImage.alt = result.spatialAlt
}

function openModal() {
  modal.hidden = false
  closeModalBtn.focus()
}

function closeModal() {
  modal.hidden = true
  runPipelineBtn.focus()
}

buttons.forEach((button) => {
  button.addEventListener('click', () => setLevel(button.dataset.level))
})

runPipelineBtn.addEventListener('click', openModal)
closeModalBtn.addEventListener('click', closeModal)

modal.addEventListener('click', (event) => {
  if (event.target === modal) {
    closeModal()
  }
})

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && !modal.hidden) {
    closeModal()
  }
})

document.querySelectorAll(`a[href="${repoUrl}"], a[href="${datasetUrl}"]`).forEach((link) => {
  link.rel = 'noreferrer'
})
