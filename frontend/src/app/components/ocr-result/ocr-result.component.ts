import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { NgChartsModule } from 'ng2-charts';
@Component({
  selector: 'app-ocr-result',
  imports: [CommonModule, NgChartsModule],
  templateUrl: './ocr-result.component.html',
  styleUrl: './ocr-result.component.scss',
})
export class OcrResultComponent {
  @Input() text: string = '';
  @Input() structured: any;
}
