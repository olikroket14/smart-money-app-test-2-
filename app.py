import { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { awardCoins, COIN_REWARDS } from "../lib/coins";
import { motion } from "framer-motion";
import { Trophy, Zap, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { challenges, getDifficultyColor, getChallengeById } from "../lib/challenges";

export default function Challenges() {
  const [progressList, setProgressList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("beschikbaar");

  async function loadProgress() {
    const data = await base44.entities.ChallengeProgress.list("-created_date", 100);
    setProgressList(data);
    setLoading(false);
  }

  useEffect(() => {
    loadProgress();
  }, []);

  async function startChallenge(challengeId) {
    await base44.entities.ChallengeProgress.create({
      challenge_id: challengeId,
      status: "active",
      progress: 0,
      started_date: new Date().toISOString().split("T")[0],
      xp_earned: 0,
    });
    loadProgress();
  }

  async function updateProgress(progressItem, newProgress) {
    const challenge = getChallengeById(progressItem.challenge_id);
    const isComplete = newProgress >= 100;
    if (isComplete) {
      await awardCoins(COIN_REWARDS.challenge_complete, `Challenge voltooid: ${challenge?.title}`);
    }
    await base44.entities.ChallengeProgress.update(progressItem.id, {
      progress: Math.min(newProgress, 100),
      status: isComplete ? "completed" : "active",
      completed_date: isComplete ? new Date().toISOString().split("T")[0] : undefined,
      xp_earned: isComplete ? challenge?.xp || 0 : 0,
    });
    loadProgress();
  }

  const activeProgressIds = progressList.filter(p => p.status === "active").map(p => p.challenge_id);
  const completedProgressIds = progressList.filter(p => p.status === "completed").map(p => p.challenge_id);
  const available = challenges.filter(c => !activeProgressIds.includes(c.id) && !completedProgressIds.includes(c.id));
  const activeChallenges = progressList.filter(p => p.status === "active");
  const completedChallenges = progressList.filter(p => p.status === "completed");

  const totalXP = completedChallenges.reduce((s, p) => s + (p.xp_earned || 0), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="px-5 pt-14 pb-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold font-heading">Challenges</h1>
        <div className="flex items-center gap-1.5 bg-accent/20 text-accent px-3 py-1.5 rounded-full">
          <Zap className="w-4 h-4" />
          <span className="text-sm font-bold">{totalXP} XP</span>
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        {[
          { value: "beschikbaar", label: `Beschikbaar (${available.length})` },
          { value: "actief", label: `Actief (${activeChallenges.length})` },
          { value: "klaar", label: `Klaar (${completedChallenges.length})` },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={`px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === tab.value
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "beschikbaar" && (
        <div className="space-y-3">
          {available.map((challenge, i) => (
            <motion.div
              key={challenge.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-card rounded-2xl border border-border/50 p-4"
            >
              <div className="flex items-start gap-3 mb-3">
                <span className="text-3xl">{challenge.emoji}</span>
                <div className="flex-1">
                  <h4 className="font-semibold mb-0.5">{challenge.title}</h4>
                  <p className="text-xs text-muted-foreground leading-relaxed">{challenge.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 mb-3">
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${getDifficultyColor(challenge.difficulty)}`}>
                  {challenge.difficulty}
                </span>
                <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {challenge.duration}
                </span>
                <span className="text-[10px] text-accent font-semibold flex items-center gap-1">
                  <Zap className="w-3 h-3" /> {challenge.xp} XP
                </span>
              </div>
              <Button onClick={() => startChallenge(challenge.id)} className="w-full rounded-xl" size="sm">
                Start challenge
              </Button>
            </motion.div>
          ))}
        </div>
      )}

      {activeTab === "actief" && (
        <div className="space-y-3">
          {activeChallenges.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-4xl mb-2">🏆</p>
              <p className="text-sm text-muted-foreground">Geen actieve challenges. Start er een!</p>
            </div>
          ) : (
            activeChallenges.map((prog) => {
              const challenge = getChallengeById(prog.challenge_id);
              if (!challenge) return null;
              return (
                <motion.div
                  key={prog.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-card rounded-2xl border border-border/50 p-4"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">{challenge.emoji}</span>
                    <div className="flex-1">
                      <h4 className="font-semibold text-sm">{challenge.title}</h4>
                      <p className="text-xs text-muted-foreground">{prog.progress}% voltooid</p>
                    </div>
                  </div>
                  <Progress value={prog.progress} className="h-2.5 mb-3" />
                  <div className="flex gap-2">
                    <Button
                      onClick={() => updateProgress(prog, prog.progress + 25)}
                      size="sm"
                      className="flex-1 rounded-xl text-xs"
                    >
                      +25% voortgang
                    </Button>
                    <Button
                      onClick={() => updateProgress(prog, 100)}
                      size="sm"
                      variant="outline"
                      className="rounded-xl text-xs"
                    >
                      ✅ Voltooid
                    </Button>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      )}

      {activeTab === "klaar" && (
        <div className="space-y-3">
          {completedChallenges.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-4xl mb-2">⭐</p>
              <p className="text-sm text-muted-foreground">Nog geen challenges voltooid</p>
            </div>
          ) : (
            completedChallenges.map((prog) => {
              const challenge = getChallengeById(prog.challenge_id);
              if (!challenge) return null;
              return (
                <div
                  key={prog.id}
                  className="bg-secondary/10 rounded-2xl p-4 flex items-center gap-3"
                >
                  <span className="text-2xl">{challenge.emoji}</span>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm">{challenge.title}</h4>
                    <p className="text-xs text-secondary">+{prog.xp_earned} XP verdiend!</p>
                  </div>
                  <Trophy className="w-5 h-5 text-secondary" />
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}