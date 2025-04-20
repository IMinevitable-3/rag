import { Component, ViewChild, ElementRef } from '@angular/core';
import { OcrService } from '../../services/ocr.service';
import { CommonModule } from '@angular/common';
import { OcrResultComponent } from '../ocr-result/ocr-result.component';
@Component({
  selector: 'app-ocr',
  imports: [CommonModule, OcrResultComponent],
  templateUrl: './ocr.component.html',
  styleUrl: './ocr.component.scss',
})
export class OcrComponent {
  extractedText = '';
  structuredData = {};
  loading = false;
  error = '';

  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  constructor(private ocrService: OcrService) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length) {
      this.uploadFile(input.files[0]);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    (event.currentTarget as HTMLElement).classList.add('dragover');
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    (event.currentTarget as HTMLElement).classList.remove('dragover');

    if (event.dataTransfer?.files?.length) {
      this.uploadFile(event.dataTransfer.files[0]);
    }
  }

  uploadFile(file: File) {
    this.extractedText = '';
    this.error = '';
    this.loading = true;

    this.ocrService.uploadImageAndExtractText(file).subscribe({
      next: (res) => {
        this.extractedText = res.text;
        this.structuredData = res.structured;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to process image.';
        console.error(err);
        this.loading = false;
      },
    });
  }
}
