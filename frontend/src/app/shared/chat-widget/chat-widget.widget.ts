import {
  AfterViewChecked,
  Component,
  ElementRef,
  ViewChild,
  OnInit
} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { use } from 'marked';

interface User {
  id: number;
  pid: number;
  onyen: string;
  first_name: string;
  last_name: string;
  email: string;
  pronouns: string;
  github: string;
  github_id?: number;
  github_avatar?: string;
  accepted_community_agreement: boolean;
  bio?: string;
  linkedin?: string;
  website?: string;
}

@Component({
  selector: 'chat-widget',
  templateUrl: './chat-widget.widget.html',
  styleUrls: ['./chat-widget.widget.css']
})
export class ChatWidget implements AfterViewChecked, OnInit {
  constructor(private http: HttpClient) {
    this.fetchUser();
  }
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  isChatOpen = false;
  userMessage = '';
  messages: { id: number; text: string; sender: 'user' | 'bot'; time: Date }[] =
    [
      {
        id: 1,
        text: "Hi! I'm ChadGPT. How can I help you today?",
        sender: 'bot',
        time: new Date(Date.now())
      }
    ];
  private messageId = 2;
  private shouldScroll = false;
  private justOpenedChat = false;
  ratings: { [messageId: number]: number } = {};
  stars = [1, 2, 3, 4, 5];
  userId: number | null = null;

  setRating(star: number, messageId: number): void {
    this.ratings[messageId] = star;
    localStorage.setItem('chatRatings', JSON.stringify(this.ratings));
  }

  isReservationConfirmation(message: string): boolean {
    const pattern = /^✅ Room .+ reserved from .+ to .+$/;
    return pattern.test(message);
  }
  isReservationChangeConfirmation(message: string): boolean {
    const pattern =
      /^Reservation .+ was cancelled\. New reservation created for room .+ from .+ to .+.$/;
    return pattern.test(message);
  }

  isReservationCancellationConfirmation(message: string): boolean {
    const pattern = /^ Reservation .+ has been cancelled\.$/;
    return pattern.test(message);
  }

  fetchUser() {
    const token = localStorage.getItem('bearerToken');
    if (!token) return;

    this.http
      .get<User>('/api/user/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .subscribe({
        next: (user) => {
          this.userId = user.id;
          console.log('Logged in as:', user);
        },
        error: (err) => {
          console.error('Unable to fetch user:', err);
        }
      });
  }

  toggleChat(): void {
    this.isChatOpen = !this.isChatOpen;
    if (this.isChatOpen) {
      this.shouldScroll = true;
      this.justOpenedChat = true;
    } else if (!this.isChatOpen) {
      this.sendConversationToDatabase();
    }
  }

  loadRatingsFromLocalStorage(): void {
    const stored = localStorage.getItem('chatRatings');
    if (stored) {
      this.ratings = JSON.parse(stored);
    }
  }

  ngOnInit(): void {
    this.loadMessagesFromLocalStorage();
    this.loadRatingsFromLocalStorage();
  }

  sendMessage(): void {
    const trimmed = this.userMessage.trim();
    if (!trimmed) return;

    this.messages.push({
      id: this.messageId++,
      text: trimmed,
      sender: 'user',
      time: new Date(Date.now())
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
          sender: 'bot',
          time: new Date(Date.now())
        });
        this.saveMessagesToLocalStorage();
        this.shouldScroll = true;
      })
      .catch((err) => {
        this.messages.push({
          id: this.messageId++,
          text: 'I seem to have experienced an error. Report it here: {add link}',
          sender: 'bot',
          time: new Date(Date.now())
        });
        this.shouldScroll = true;
        console.error(err);
      });
  }

  saveMessagesToLocalStorage(): void {
    localStorage.setItem('chatMessages', JSON.stringify(this.messages));
    localStorage.setItem('chatMessageId', this.messageId.toString());
  }

  sendConversationToDatabase(): void {
    const storedRatings = localStorage.getItem('chatRatings');
    const ratings = storedRatings ? JSON.parse(storedRatings) : {};
    const maxRatedMessage = Object.keys(ratings).reduce(
      (max, key) => (ratings[key] > ratings[max] ? key : max),
      Object.keys(ratings)[0] || '0'
    );

    const conversation = {
      created_at: new Date().toISOString(),
      user_id: this.userId,
      chat_history: this.messages.map((m) => m.text),
      rating: ratings[maxRatedMessage] || 0,
      feedback: '',
      outcome: 'Requested Information'
    };

    const token = localStorage.getItem('bearerToken');

    this.http
      .post('/api/conversations', conversation, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .subscribe({
        next: (res) => console.log('Conversation saved:', res),
        error: (err) => console.error('Failed to save conversation:', err)
      });
    console.log('Sending conversation to DB:', conversation);
  }

  loadMessagesFromLocalStorage(): void {
    const storedMessages = localStorage.getItem('chatMessages');
    const storedId = localStorage.getItem('chatMessageId');

    if (storedMessages) {
      const now = new Date();
      const parsed = JSON.parse(storedMessages);

      this.messages = parsed.filter((m: any) => {
        const messageTime = new Date(m.time);
        const diff = now.getTime() - messageTime.getTime();
        return diff < 24 * 60 * 60 * 1000;
      });
    }

    if (storedId) {
      this.messageId = parseInt(storedId, 10);
    }
    this.saveMessagesToLocalStorage();
  }

  clearMessages(): void {
    localStorage.removeItem('chatMessages');
    localStorage.removeItem('chatMessageId');
    localStorage.removeItem('chatRatings');
    this.messages = [
      {
        id: 1,
        text: "Hi! I'm ChadGPT. How can I help you today?",
        sender: 'bot',
        time: new Date(Date.now())
      }
    ];
    this.messageId = 2;
    this.ratings = {};
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
