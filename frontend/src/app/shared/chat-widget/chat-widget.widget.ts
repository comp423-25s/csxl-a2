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
  private justOpenedChat = false;
  rating = 0;
  stars = [1, 2, 3, 4, 5];

  setRating(star: number): void {
    this.rating = star;
  }

  isReservationConfirmation(message: string): boolean {
    const pattern = /^✅ Room .+ reserved from .+ to .+$/;
    return pattern.test(message);
  }

  handleRating(): void {
    alert('Thank you for your feedback!');
  }

  toggleChat(): void {
    this.isChatOpen = !this.isChatOpen;
    if (this.isChatOpen) {
      this.shouldScroll = true;
      this.justOpenedChat = true;
    }
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
    const recentMessages = this.messages.slice(-10);

    const openaiFormattedHistory = recentMessages.map((m) => ({
      role: m.sender === 'bot' ? 'assistant' : 'user',
      content: m.text
    }));

    const token = localStorage.getItem('bearerToken');
    console.log('Bearer token being used:', token);
    console.log(
      JSON.stringify(
        {
          message: trimmed,
          history: openaiFormattedHistory
        },
        null,
        2
      )
    );

    fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        message: trimmed,
        history: openaiFormattedHistory
      })
    })
      .then(async (res) => {
        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Error ${res.status}: ${errorText}`);
        }
        return res.json();
      })
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
          text: 'I seem to have experienced an error. Report it here: {add link}',
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
    localStorage.removeItem('chatMesasgeId');
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom(this.justOpenedChat);
      this.shouldScroll = false;
      this.justOpenedChat = false;
    }
  }

  private scrollToBottom(instant = false): void {
    try {
      this.scrollContainer.nativeElement.scrollTo({
        top: this.scrollContainer.nativeElement.scrollHeight,
        behavior: instant ? 'auto' : 'smooth'
      });
    } catch (err) {
      console.error('Scroll error', err);
    }
  }
}
