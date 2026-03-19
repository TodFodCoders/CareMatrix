import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  ReactNode,
} from "react";
import { registerHospital, updateCapacity } from "./api";

const DEPARTMENTS = ["Emergency", "ICU", "Surgery", "Radiology"];

type HospitalCtx = {
  hospitalId: string | null;
  ready: boolean;
};

const Ctx = createContext<HospitalCtx>({ hospitalId: null, ready: false });

async function seedCapacity(id: string) {
  await Promise.all(
    DEPARTMENTS.map((dept) => updateCapacity(id, dept, 20, 20)),
  );
}

export function HospitalProvider({ children }: { children: ReactNode }) {
  const [hospitalId, setHospitalId] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const init = useRef(false);

  useEffect(() => {
    if (init.current) return;
    init.current = true;

    const stored = localStorage.getItem("cm_hospital_id");
    if (stored) {
      setHospitalId(stored);
      setReady(true);
      return;
    }
    registerHospital("CareMatrix General Hospital", 28.6, 77.1)
      .then(async (res) => {
        localStorage.setItem("cm_hospital_id", res.id);
        await seedCapacity(res.id);
        setHospitalId(res.id);
      })
      .finally(() => setReady(true));
  }, []);

  return <Ctx.Provider value={{ hospitalId, ready }}>{children}</Ctx.Provider>;
}

export function useHospital() {
  return useContext(Ctx);
}
