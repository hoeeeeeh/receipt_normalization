import  { writable } from 'svelte/store'

export const dropZoneBackgroundColor = writable("#FFFFFF");
export const dropZoneColor = writable("#6B6B6B");
export const dropZoneWidth = writable("0px");
export const dropZoneDialogDisplay = writable("flex")
export const dropFileName = writable("")
export const dropZoneBackgroundImage = writable("")

export const scanboxBackgroundColor = writable("#BCBCBC")

export let resultData = writable([
    ['0', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1'],
    ['1', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
])

export let uploadedFile = writable();

export let mode = writable("ocr");