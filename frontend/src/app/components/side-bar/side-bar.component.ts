import {
  Component,
  EventEmitter,
  OnInit,
  OnDestroy,
  Output,
} from '@angular/core';
import { OcrService } from '../../services/ocr.service';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-side-bar',
  imports: [CommonModule],
  templateUrl: './side-bar.component.html',
  styleUrl: './side-bar.component.scss',
})
export class SideBarComponent implements OnInit, OnDestroy {
  collapsed = false;
  history: any[] = [];
  @Output() collapsedChange = new EventEmitter<boolean>();
  private historySub?: Subscription;
  private updateSub?: Subscription;

  constructor(private ocrService: OcrService) {}

  toggleCollapse() {
    this.collapsed = !this.collapsed;
    this.collapsedChange.emit(this.collapsed);
  }

  ngOnInit() {
    this.loadHistory();

    this.updateSub = this.ocrService.onHistoryUpdated().subscribe(() => {
      this.loadHistory();
    });
  }

  loadHistory() {
    this.historySub = this.ocrService.getHistory().subscribe({
      next: (res) => (this.history = res.history || []),
      error: (err) => console.error('Failed to load history', err),
    });
  }

  ngOnDestroy() {
    this.historySub?.unsubscribe();
    this.updateSub?.unsubscribe();
  }
}
