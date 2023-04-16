#include "Stk.h"
#include "SineWave.h"
#include "ADSR.h"
#include "JCRev.h"
#include "DelayL.h"
#include "Delay.h"
#include "Envelope.h"
#include "BiQuad.h"
#include "Blit.h"

extern "C" {
    stk::SineWave* SineWave_ctor() {
        stk::SineWave* sine = new stk::SineWave();
        return sine;
    }

    void SineWave_setRate(stk::SineWave* sine, double rate) {
        sine->setRate(rate);
    }

    void SineWave_setFrequency(stk::SineWave* sine, double frequency) {
        sine->setFrequency(frequency);
    }

    double SineWave_tick(stk::SineWave* sine) {
        return sine->tick();
    }

    void SineWave_dtor(stk::SineWave* sine) {
        delete sine;
    }

    stk::ADSR* ADSR_ctor() {
        stk::ADSR* adsr = new stk::ADSR();
        return adsr;
    }

    void ADSR_setAllTimes(stk::ADSR* adsr, double attack, double decay, double sustain, double release) {
        adsr->setAllTimes(attack, decay, sustain, release);
    }

    void ADSR_keyOn(stk::ADSR* adsr) {
        adsr->keyOn();
    }

    void ADSR_keyOff(stk::ADSR* adsr) {
        adsr->keyOff();
    }

    double ADSR_tick(stk::ADSR* adsr) {
        return adsr->tick();
    }

    void ADSR_dtor(stk::ADSR* adsr) {
        delete adsr;
    }

    stk::JCRev* JCRev_ctor() {
        stk::JCRev* jcRev = new stk::JCRev();
        return jcRev;
    }

    void JCRev_setEffectMix(stk::JCRev* jcRev, double mix) {
        jcRev->setEffectMix(mix);
    }

    double JCRev_tick(stk::JCRev* jcRev, double input) {
        return jcRev->tick(input);
    }

    void JCRev_dtor(stk::JCRev* jcRev) {
        delete jcRev;
    }

    stk::DelayL* DelayL_ctor() {
        stk::DelayL* delayL = new stk::DelayL();
        return delayL;
    }

    void DelayL_setMaximumDelay(stk::DelayL* delayL, unsigned long delay) {
        delayL->setMaximumDelay(delay);
    }

    void DelayL_setDelay(stk::DelayL* delayL, double delay) {
        delayL->setDelay(delay);
    }

    double DelayL_tick(stk::DelayL* delayL, double input) {
        return delayL->tick(input);
    }

    void DelayL_dtor(stk::DelayL* delayL) {
        delete delayL;
    }

    stk::Delay* Delay_ctor() {
        stk::Delay* delay = new stk::Delay();
        return delay;
    }

    void Delay_setDelay(stk::Delay* delay, unsigned long delay_) {
        delay->setDelay(delay_);
    }

    double Delay_tick(stk::Delay* delay, double input) {
        return delay->tick(input);
    }

    void Delay_dtor(stk::Delay* delay) {
        delete delay;
    }

    stk::Envelope* Envelope_ctor() {
        stk::Envelope* envelope = new stk::Envelope();
        return envelope;
    }

    void Envelope_setRate(stk::Envelope* envelope, double rate) {
        envelope->setRate(rate);
    }

    void Envelope_keyOn(stk::Envelope* envelope) {
        envelope->keyOn();
    }

    void Envelope_keyOff(stk::Envelope* envelope) {
        envelope->keyOff();
    }

    double Envelope_tick(stk::Envelope* envelope) {
        return envelope->tick();
    }

    void Envelope_dtor(stk::Envelope* envelope) {
        delete envelope;
    }

    stk::BiQuad* BiQuad_ctor() {
        stk::BiQuad* biQuad = new stk::BiQuad();
        return biQuad;
    }

    void BiQuad_setResonance(stk::BiQuad* biQuad, double frequency, double radius, bool normalize) {
        biQuad->setResonance(frequency, radius, normalize);
    }

    void BiQuad_setEqualGainZeroes(stk::BiQuad* biQuad) {
        biQuad->setEqualGainZeroes();
    }

    double BiQuad_tick(stk::BiQuad* biQuad, double input) {
        return biQuad->tick(input);
    }

    void BiQuad_dtor(stk::BiQuad* biQuad) {
        delete biQuad;
    }

    stk::Blit* Blit_ctor() {
        stk::Blit* blit = new stk::Blit();
        return blit;
    }

    void Blit_setFrequency(stk::Blit* blit, double frequency) {
        blit->setFrequency(frequency);
    }

    void Blit_setHarmonics(stk::Blit* blit, double harmonics) {
        blit->setHarmonics(harmonics);
    }

    double Blit_tick(stk::Blit* blit) {
        return blit->tick();
    }

    void Blit_dtor(stk::Blit* blit) {
        delete blit;
    }

}
