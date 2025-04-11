import {
  AfterViewChecked,
  Component,
  ElementRef,
  ViewChild,
  OnInit
} from '@angular/core';

@Component({
  selector: 'chat-widget',
  templateUrl: './chat-widget.widget.html',
  styleUrls: ['./chat-widget.widget.css']
})
export class ChatWidget implements AfterViewChecked, OnInit {
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  isChatOpen = false;
  userMessage = '';
  messages: { id: number; text: string; sender: 'user' | 'bot' }[] = [
    { id: 1, text: "Hi! I'm ChadGPT. How can I help you today?", sender: 'bot' }
  ];
  private messageId = 2;
  private shouldScroll = false;

  toggleChat(): void {
    this.isChatOpen = !this.isChatOpen;
    this.scrollToBottom();
  }

  ngOnInit(): void {
    this.loadMessagesFromLocalStorage();
  }
  sendMessage(): void {
    const trimmed = this.userMessage.trim();
    if (!trimmed) return;

    this.messages.push({
      id: this.messageId++,
      text: trimmed,
      sender: 'user'
    });
    this.saveMessagesToLocalStorage();

    this.userMessage = '';
    this.shouldScroll = true;

    const token = localStorage.getItem('bearerToken');
    console.log('Bearer token being used:', token);

    fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ message: trimmed })
    })
      .then((res) => res.json())
      .then((data) => {
        this.messages.push({
          id: this.messageId++,
          text: data.response,
          sender: 'bot'
        });
        this.saveMessagesToLocalStorage();
        this.shouldScroll = true;
      })
      .catch((err) => {
        this.messages.push({
          id: this.messageId++,
          text: "Sorry, I couldn't reach the chatbot backend.",
          sender: 'bot'
        });
        this.shouldScroll = true;
        console.error(err);
      });
  }

  saveMessagesToLocalStorage(): void {
    localStorage.setItem('chatMessages', JSON.stringify(this.messages));
    localStorage.setItem('chatMessageId', this.messageId.toString());
  }
  loadMessagesFromLocalStorage(): void {
    const storedMessages = localStorage.getItem('chatMessages');
    const storedId = localStorage.getItem('chatMessageId');
    if (storedMessages) {
      this.messages = JSON.parse(storedMessages);
    }
    if (storedId) {
      this.messageId = parseInt(storedId, 10);
    }
  }
  clearMessages(): void {
    this.messages = [];
    localStorage.removeItem('chatMessages');
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  private scrollToBottom(): void {
    try {
      this.scrollContainer.nativeElement.scrollTo({
        top: this.scrollContainer.nativeElement.scrollHeight,
        behavior: 'smooth'
      });
    } catch (err) {
      console.error('Scroll error', err);
    }
  }
}
