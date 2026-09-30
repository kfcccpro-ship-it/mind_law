const SHEET_COMPLETIONS = 'COMPLETIONS';
const SHEET_ROSTER = 'ROSTER';

function setup() {
  const props = PropertiesService.getScriptProperties();
  let id = props.getProperty('SHEET_ID');
  const ss = id ? SpreadsheetApp.openById(id) : SpreadsheetApp.create('간부자격 DAILY 완료현황');
  props.setProperty('SHEET_ID', ss.getId());
  if (!props.getProperty('ADMIN_KEY')) props.setProperty('ADMIN_KEY', Utilities.getUuid().replace(/-/g, ''));
  ensureSheets_(ss);
  return { sheetUrl: ss.getUrl(), adminKey: props.getProperty('ADMIN_KEY') };
}

function ensureSheets_(ss) {
  const c = ss.getSheetByName(SHEET_COMPLETIONS) || ss.insertSheet(SHEET_COMPLETIONS);
  const r = ss.getSheetByName(SHEET_ROSTER) || ss.insertSheet(SHEET_ROSTER);
  const headers = ['timestamp','date','day','nickname','total','mastered','firstCorrect','dontKnowCount','remediationCount','finalRetestCount','finalRetestPassed','completionCode','startedAt','completedAt'];
  if (c.getLastRow() === 0) c.appendRow(headers);
  if (r.getLastRow() === 0) r.appendRow(['nickname','active','memo']);
}

function ss_() {
  const id = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  if (!id) throw new Error('setup()을 먼저 실행하세요.');
  const ss = SpreadsheetApp.openById(id);
  ensureSheets_(ss);
  return ss;
}

function out_(obj, callback) {
  const json = JSON.stringify(obj);
  if (callback && /^[a-zA-Z_$][\w$\.]*$/.test(callback)) {
    return ContentService.createTextOutput(callback + '(' + json + ');')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const p = e.parameter || {};
    if (p.action !== 'complete') return out_({ok:false,error:'unknown action'});
    const total = Number(p.total || 0);
    const mastered = Number(p.mastered || 0);
    const nick = String(p.nickname || '').trim();
    const date = String(p.date || '').trim();
    if (!nick || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(date)) return out_({ok:false,error:'invalid nickname/date'});
    if (total < 1 || mastered !== total) return out_({ok:false,error:'not fully mastered'});

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      const sh = ss_().getSheetByName(SHEET_COMPLETIONS);
      const vals = sh.getDataRange().getValues();
      let row = 0;
      for (let i = 1; i < vals.length; i++) {
        if (String(vals[i][1]) === date && String(vals[i][3]).trim() === nick) { row = i + 1; break; }
      }
      const rec = [
        new Date(), date, Number(p.day || 0), nick, total, mastered,
        Number(p.firstCorrect || 0), Number(p.dontKnowCount || 0),
        Number(p.remediationCount || 0), Number(p.finalRetestCount || 0),
        Number(p.finalRetestPassed || 0), String(p.completionCode || ''),
        String(p.startedAt || ''), String(p.completedAt || '')
      ];
      if (row) sh.getRange(row, 1, 1, rec.length).setValues([rec]);
      else sh.appendRow(rec);
    } finally {
      lock.releaseLock();
    }
    return out_({ok:true});
  } catch (err) {
    return out_({ok:false,error:String(err)});
  }
}

function doGet(e) {
  try {
    const p = e.parameter || {};
    const cb = p.callback;
    if (p.action === 'health') return out_({ok:true,service:'MG DAILY completion API'}, cb);
    if (p.action !== 'summary') return out_({ok:false,error:'unknown action'}, cb);

    const key = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY');
    if (!key || String(p.key || '') !== key) return out_({ok:false,error:'unauthorized'}, cb);

    const date = String(p.date || '').trim();
    const ss = ss_();
    const c = ss.getSheetByName(SHEET_COMPLETIONS);
    const r = ss.getSheetByName(SHEET_ROSTER);
    const cv = c.getDataRange().getValues();
    const rv = r.getDataRange().getValues();
    const completed = [];

    for (let i = 1; i < cv.length; i++) {
      if (!date || String(cv[i][1]) === date) {
        completed.push({
          date:String(cv[i][1]), day:cv[i][2], nickname:String(cv[i][3]),
          total:cv[i][4], firstCorrect:cv[i][6], dontKnowCount:cv[i][7],
          remediationCount:cv[i][8], finalRetestCount:cv[i][9], finalRetestPassed:cv[i][10],
          completionCode:String(cv[i][11]), completedAt:String(cv[i][13])
        });
      }
    }

    const roster = rv.slice(1)
      .filter(x => String(x[0]).trim() && String(x[1]).toLowerCase() !== 'false')
      .map(x => String(x[0]).trim());
    const doneSet = new Set(completed.filter(x => !date || x.date === date).map(x => x.nickname));
    const missing = roster.filter(x => !doneSet.has(x));

    return out_({
      ok:true, date, rosterCount:roster.length,
      completedCount:date ? doneSet.size : completed.length,
      missingCount:date ? missing.length : null,
      completed, missing
    }, cb);
  } catch (err) {
    return out_({ok:false,error:String(err)}, e.parameter && e.parameter.callback);
  }
}