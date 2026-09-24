import Dexie, { type Table } from "dexie";

export type PendingCall = {
  id?: number;
  key: string;
  payload: unknown;
  createdAt: number;
};

class SgaDatabase extends Dexie {
  pendingCalls!: Table<PendingCall, number>;

  constructor() {
    super("sga-edu-offline");
    this.version(1).stores({ pendingCalls: "++id, &key, createdAt" });
  }
}

export const db = new SgaDatabase();
